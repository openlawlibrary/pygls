############################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.                 #
# Original work licensed under the MIT License.                            #
# See ThirdPartyNotices.txt in the project root for license information.   #
# All modifications Copyright (c) Open Law Library. All rights reserved.   #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import io
import logging
import os
import pathlib
import re
from typing import Optional, Pattern, Sequence

from lsprotocol import types

from pygls.uris import urlparse, to_fs_path
from .position_codec import PositionCodec

# TODO: this is not the best e.g. we capture numbers
RE_END_WORD = re.compile("^[A-Za-z_0-9]*")
RE_START_WORD = re.compile("[A-Za-z_0-9]*$")

logger = logging.getLogger(__name__)


class TextDocument(object):
    def __init__(
        self,
        uri: str,
        source: Optional[str] = None,
        version: Optional[int] = None,
        language_id: Optional[str] = None,
        local: bool = True,
        sync_kind: types.TextDocumentSyncKind = types.TextDocumentSyncKind.Incremental,
        position_codec: Optional[PositionCodec] = None,
    ):
        self.uri = uri
        self.version = version

        if (path := to_fs_path(uri)) is None:
            _, _, path, *_ = urlparse(uri)

        self.path = path
        self.language_id = language_id
        self.filename: Optional[str] = os.path.basename(self.path)

        self._local = local
        self._source = source

        self._is_sync_kind_full = sync_kind == types.TextDocumentSyncKind.Full
        self._is_sync_kind_incremental = (
            sync_kind == types.TextDocumentSyncKind.Incremental
        )
        self._is_sync_kind_none = sync_kind == types.TextDocumentSyncKind.None_

        self._position_codec = position_codec if position_codec else PositionCodec()

    def __str__(self):
        return str(self.uri)

    @property
    def position_codec(self) -> PositionCodec:
        return self._position_codec

    def _apply_incremental_change(
        self, change: types.TextDocumentContentChangePartial
    ) -> None:
        """Apply an ``Incremental`` text change to the document"""
        lines = self.lines
        text = change.text
        change_range = change.range

        range = self._position_codec.range_from_client_units(lines, change_range)
        start_line = range.start.line
        start_col = range.start.character
        end_line = range.end.line
        end_col = range.end.character

        # Check for an edit occurring at the very end of the file
        if start_line == len(lines):
            self._source = self.source + text
            return

        new = io.StringIO()

        # Iterate over the existing document until we hit the edit range,
        # at which point we write the new text, then loop until we hit
        # the end of the range and continue writing.
        for i, line in enumerate(lines):
            if i < start_line:
                new.write(line)
                continue

            if i > end_line:
                new.write(line)
                continue

            if i == start_line:
                new.write(line[:start_col])
                new.write(text)

            if i == end_line:
                new.write(line[end_col:])

        self._source = new.getvalue()

    def _apply_full_change(self, change: types.TextDocumentContentChangeEvent) -> None:
        """Apply a ``Full`` text change to the document."""
        self._source = change.text

    def _apply_none_change(self, _: types.TextDocumentContentChangeEvent) -> None:
        """Apply a ``None`` text change to the document

        Currently does nothing, provided for consistency.
        """
        pass

    def apply_change(self, change: types.TextDocumentContentChangeEvent) -> None:
        """Apply a text change to a document, considering TextDocumentSyncKind

        Performs either
        :attr:`~lsprotocol.types.TextDocumentSyncKind.Incremental`,
        :attr:`~lsprotocol.types.TextDocumentSyncKind.Full`, or no synchronization
        based on both the client request and server capabilities.

        .. admonition:: ``Incremental`` versus ``Full`` synchronization

           Even if a server accepts ``Incremantal`` SyncKinds, clients may request
           a ``Full`` SyncKind. In LSP 3.x, clients make this request by omitting
           both Range and RangeLength from their request. Consequently, the
           attributes "range" and "rangeLength" will be missing from ``Full``
           content update client requests in the pygls Python library.

        """
        if isinstance(change, types.TextDocumentContentChangePartial):
            if self._is_sync_kind_incremental:
                self._apply_incremental_change(change)
                return
            # Log an error, but still perform full update to preserve existing
            # assumptions in test_document/test_document_full_edit. Test breaks
            # otherwise, and fixing the tests would require a broader fix to
            # protocol.py.
            logger.error(
                "Unsupported client-provided TextDocumentContentChangeEvent. "
                "Please update / submit a Pull Request to your LSP client."
            )

        if self._is_sync_kind_none:
            self._apply_none_change(change)
        else:
            self._apply_full_change(change)

    @property
    def lines(self) -> Sequence[str]:
        return tuple(self.source.splitlines(True))

    def offset_at_position(self, client_position: types.Position) -> int:
        """
        Convert client_position to an index into self.source.

        The index is the number of code points preceding the client_position in self.source.

        Example in a code action request handler:
            selected_string = document.source[
                document.offset_at_position(params.range.start) : document.offset_at_position(params.range.end)
            ]
        """
        lines = self.lines
        server_position = self._position_codec.position_from_client_units(
            lines, client_position
        )
        row, col = server_position.line, server_position.character
        return col + sum(len(line) for line in lines[:row])

    @property
    def source(self) -> str:
        if self._source is None and self.path is not None:
            return pathlib.Path(self.path).read_text(encoding="utf-8")

        return self._source or ""

    def word_at_position(
        self,
        client_position: types.Position,
        re_start_word: Pattern[str] = RE_START_WORD,
        re_end_word: Pattern[str] = RE_END_WORD,
    ) -> str:
        """Return the word at position.

        The word is constructed in two halves, the first half is found by taking
        the first match of ``re_start_word`` on the line up until
        ``position.character``.

        The second half is found by taking ``position.character`` up until the
        last match of ``re_end_word`` on the line.

        :func:`python:re.findall` is used to find the matches.

        Parameters
        ----------
        position
           The line and character offset.

        re_start_word
           The regular expression for extracting the word backward from
           position. The default pattern is ``[A-Za-z_0-9]*$``.

        re_end_word
           The regular expression for extracting the word forward from
           position. The default pattern is ``^[A-Za-z_0-9]*``.

        Returns
        -------
        str
           The word (obtained by concatenating the two matches) at position.
        """
        lines = self.lines
        if client_position.line >= len(lines):
            return ""

        server_position = self._position_codec.position_from_client_units(
            lines, client_position
        )
        row, col = server_position.line, server_position.character
        line = lines[row]
        # Split word in two
        start = line[:col]
        end = line[col:]

        # Take end of start and start of end to find word
        # These are guaranteed to match, even if they match the empty string
        m_start = re_start_word.findall(start)
        m_end = re_end_word.findall(end)

        return m_start[0] + m_end[-1]
