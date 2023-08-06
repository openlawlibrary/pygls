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
import copy
import io
import logging
import os
import re
import warnings
from typing import Dict, List, Optional, Pattern

from lsprotocol import types

from pygls.uris import to_fs_path, uri_scheme

# TODO: this is not the best e.g. we capture numbers
RE_END_WORD = re.compile("^[A-Za-z_0-9]*")
RE_START_WORD = re.compile("[A-Za-z_0-9]*$")

logger = logging.getLogger(__name__)


def is_char_beyond_multilingual_plane(char: str) -> bool:
    return ord(char) > 0xFFFF


def utf16_unit_offset(chars: str):
    """Calculate the number of characters which need two utf-16 code units.

    Arguments:
        chars (str): The string to count occurrences of utf-16 code units for.
    """
    return sum(is_char_beyond_multilingual_plane(ch) for ch in chars)


def utf16_num_units(chars: str):
    """Calculate the length of `str` in utf-16 code units.

    Arguments:
        chars (str): The string to return the length in utf-16 code units for.
    """
    return len(chars) + utf16_unit_offset(chars)


def position_from_utf16(lines: List[str], position: types.Position) -> types.Position:
    """Convert the position.character from utf-16 code units to utf-32.

    A python application can't use the character member of `Position`
    directly. As per specification it is represented as a zero-based line and
    character offset based on a UTF-16 string representation.

    All characters whose code point exceeds the Basic Multilingual Plane are
    represented by 2 UTF-16 code units.

    The offset of the closing quotation mark in x="😋" is
    - 5 in UTF-16 representation
    - 4 in UTF-32 representation

    see: https://github.com/microsoft/language-server-protocol/issues/376

    Arguments:
        lines (list):
            The content of the document which the position refers to.
        position (Position):
            The line and character offset in utf-16 code units.

    Returns:
        The position with `character` being converted to utf-32 code units.
    """
    if len(lines) == 0:
        return types.Position(0, 0)
    if position.line >= len(lines):
        return types.Position(len(lines) - 1, utf16_num_units(lines[-1]))

    _line = lines[position.line]
    _line = _line.replace("\r\n", "\n")  # TODO: it's a bit of a hack
    _utf16_len = utf16_num_units(_line)
    _utf32_len = len(_line)

    if _utf16_len == 0:
        return types.Position(position.line, 0)

    _utf16_end_of_line = utf16_num_units(_line)
    if position.character > _utf16_end_of_line:
        position.character = _utf16_end_of_line - 1

    _utf16_index = 0
    utf32_index = 0
    while True:
        _is_searching_queried_position = _utf16_index < position.character
        _is_before_end_of_line = utf32_index < _utf32_len
        _is_searching_for_position = (
            _is_searching_queried_position and _is_before_end_of_line
        )
        if not _is_searching_for_position:
            break

        _current_char = _line[utf32_index]
        _is_double_width = is_char_beyond_multilingual_plane(_current_char)
        if _is_double_width:
            _utf16_index += 2
        else:
            _utf16_index += 1
        utf32_index += 1

    position = types.Position(line=position.line, character=utf32_index)
    return position


def position_to_utf16(lines: List[str], position: types.Position) -> types.Position:
    """Convert the position.character from utf-32 to utf-16 code units.

    A python application can't use the character member of `Position`
    directly as per specification it is represented as a zero-based line and
    character offset based on a UTF-16 string representation.

    All characters whose code point exceeds the Basic Multilingual Plane are
    represented by 2 UTF-16 code units.

    The offset of the closing quotation mark in x="😋" is
    - 5 in UTF-16 representation
    - 4 in UTF-32 representation

    see: https://github.com/microsoft/language-server-protocol/issues/376

    Arguments:
        lines (list):
            The content of the document which the position refers to.
        position (Position):
            The line and character offset in utf-32 code units.

    Returns:
        The position with `character` being converted to utf-16 code units.
    """
    try:
        return types.Position(
            line=position.line,
            character=position.character
            + utf16_unit_offset(lines[position.line][: position.character]),
        )
    except IndexError:
        return types.Position(line=len(lines), character=0)


def range_from_utf16(lines: List[str], range: types.Range) -> types.Range:
    """Convert range.[start|end].character from utf-16 code units to utf-32.

    Arguments:
        lines (list):
            The content of the document which the range refers to.
        range (Range):
            The line and character offset in utf-32 code units.

    Returns:
        The range with `character` offsets being converted to utf-16 code units.
    """
    range_new = types.Range(
        start=position_from_utf16(lines, range.start),
        end=position_from_utf16(lines, range.end),
    )
    return range_new


def range_to_utf16(lines: List[str], range: types.Range) -> types.Range:
    """Convert range.[start|end].character from utf-32 to utf-16 code units.

    Arguments:
        lines (list):
            The content of the document which the range refers to.
        range (Range):
            The line and character offset in utf-16 code units.

    Returns:
        The range with `character` offsets being converted to utf-32 code units.
    """
    return types.Range(
        start=position_to_utf16(lines, range.start),
        end=position_to_utf16(lines, range.end),
    )


class TextDocument(object):
    def __init__(
        self,
        uri: str,
        source: Optional[str] = None,
        version: Optional[int] = None,
        language_id: Optional[str] = None,
        local: bool = True,
        sync_kind: types.TextDocumentSyncKind = types.TextDocumentSyncKind.Incremental,
    ):
        self.uri = uri
        self.version = version
        self.path = to_fs_path(uri)
        self.language_id = language_id
        self.filename = os.path.basename(self.path)

        self._local = local
        self._source = source

        self._is_sync_kind_full = sync_kind == types.TextDocumentSyncKind.Full
        self._is_sync_kind_incremental = (
            sync_kind == types.TextDocumentSyncKind.Incremental
        )
        self._is_sync_kind_none = sync_kind == types.TextDocumentSyncKind.None_

    def __str__(self):
        return str(self.uri)

    def _apply_incremental_change(
        self, change: types.TextDocumentContentChangeEvent_Type1
    ) -> None:
        """Apply an ``Incremental`` text change to the document"""
        lines = self.lines
        text = change.text
        change_range = change.range

        range = range_from_utf16(lines, change_range)  # type: ignore
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

    def _apply_none_change(self, change: types.TextDocumentContentChangeEvent) -> None:
        """Apply a ``None`` text change to the document

        Currently does nothing, provided for consistency.
        """
        pass

    def apply_change(self, change: types.TextDocumentContentChangeEvent) -> None:
        """Apply a text change to a document, considering TextDocumentSyncKind

        Performs either ``Incremental``, ``Full``, or ``None`` synchronization based on
        both the Client request and server capabilities.

        ``Incremental`` versus ``Full`` synchronization:
            Even if a server accepts ``Incremantal`` SyncKinds, clients may request
            a ``Full`` SyncKind. In LSP 3.x, clients make this request by omitting
            both Range and RangeLength from their request. Consequently, the
            attributes "range" and "rangeLength" will be missing from ``Full``
            content update client requests in the pygls Python library.

        """
        if isinstance(change, types.TextDocumentContentChangeEvent_Type1):
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
    def lines(self) -> List[str]:
        return self.source.splitlines(True)

    def offset_at_position(self, position: types.Position) -> int:
        """Return the character offset pointed at by the given position."""
        lines = self.lines
        pos = position_from_utf16(lines, position)
        row, col = pos.line, pos.character
        return col + sum(utf16_num_units(line) for line in lines[:row])

    @property
    def source(self) -> str:
        if self._source is None:
            with io.open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        return self._source

    def word_at_position(
        self,
        position: types.Position,
        re_start_word: Pattern = RE_START_WORD,
        re_end_word: Pattern = RE_END_WORD,
    ) -> str:
        """Return the word at position.

        Arguments:
            position (Position):
                The line and character offset.
            re_start_word (Pattern):
                The regular expression for extracting the word backward from
                position.  Specifically, the first match from a re.findall
                call on the line up to the character value of position.  The
                default pattern is '[A-Za-z_0-9]*$'.
            re_end_word (Pattern):
                The regular expression for extracting the word forward from
                position.  Specifically, the last match from a re.findall
                call on the line from the character value of position.  The
                default pattern is '^[A-Za-z_0-9]*'.

        Returns:
            The word (obtained by concatenating the two matches) at position.
        """
        lines = self.lines
        if position.line >= len(lines):
            return ""

        pos = position_from_utf16(lines, position)
        row, col = pos.line, pos.character
        line = lines[row]
        # Split word in two
        start = line[:col]
        end = line[col:]

        # Take end of start and start of end to find word
        # These are guaranteed to match, even if they match the empty string
        m_start = re_start_word.findall(start)
        m_end = re_end_word.findall(end)

        return m_start[0] + m_end[-1]


# For backwards compatibility
Document = TextDocument


class Workspace(object):
    def __init__(self, root_uri, sync_kind=None, workspace_folders=None):
        self._root_uri = root_uri
        self._root_uri_scheme = uri_scheme(self._root_uri)
        self._root_path = to_fs_path(self._root_uri)
        self._sync_kind = sync_kind
        self._folders = {}
        self._text_documents: Dict[str, TextDocument] = {}
        self._notebook_documents: Dict[str, types.NotebookDocument] = {}

        # Used to lookup notebooks which contain a given cell.
        self._cell_in_notebook: Dict[str, str] = {}

        if workspace_folders is not None:
            for folder in workspace_folders:
                self.add_folder(folder)

    def _create_text_document(
        self,
        doc_uri: str,
        source: Optional[str] = None,
        version: Optional[int] = None,
        language_id: Optional[str] = None,
    ) -> TextDocument:
        return TextDocument(
            doc_uri,
            source=source,
            version=version,
            language_id=language_id,
            sync_kind=self._sync_kind,
        )

    def add_folder(self, folder: types.WorkspaceFolder):
        self._folders[folder.uri] = folder

    @property
    def documents(self):
        warnings.warn(
            "'workspace.documents' has been deprecated, use "
            "'workspace.text_documents' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.text_documents

    @property
    def notebook_documents(self):
        return self._notebook_documents

    @property
    def text_documents(self):
        return self._text_documents

    @property
    def folders(self):
        return self._folders

    def get_notebook_document(
        self, *, notebook_uri: Optional[str] = None, cell_uri: Optional[str] = None
    ) -> Optional[types.NotebookDocument]:
        """Return the notebook corresponding with the given uri.

        If both ``notebook_uri`` and ``cell_uri`` are given, ``notebook_uri`` takes
        precedence.

        Parameters
        ----------
        notebook_uri
           If given, return the notebook document with the given uri.

        cell_uri
           If given, return the notebook document which contains a cell with the
           given uri

        Returns
        -------
        Optional[NotebookDocument]
           The requested notebook document if found, ``None`` otherwise.
        """
        if notebook_uri is not None:
            return self._notebook_documents.get(notebook_uri)

        notebook_uri = self._cell_in_notebook.get(cell_uri)
        return self._notebook_documents.get(notebook_uri)

    def get_text_document(self, doc_uri: str) -> TextDocument:
        """
        Return a managed document if-present,
        else create one pointing at disk.

        See https://github.com/Microsoft/language-server-protocol/issues/177
        """
        return self._text_documents.get(doc_uri) or self._create_text_document(doc_uri)

    def is_local(self):
        return (
            self._root_uri_scheme == "" or self._root_uri_scheme == "file"
        ) and os.path.exists(self._root_path)

    def put_notebook_document(self, params: types.DidOpenNotebookDocumentParams):
        notebook = params.notebook_document

        # Create a fresh instance to ensure our copy cannot be accidentally modified.
        self._notebook_documents[notebook.uri] = copy.deepcopy(notebook)

        for cell_document in params.cell_text_documents:
            self.put_text_document(cell_document, notebook_uri=notebook.uri)

    def put_text_document(
        self,
        text_document: types.TextDocumentItem,
        notebook_uri: Optional[str] = None,
    ):
        """Add a text document to the workspace.

        Parameters
        ----------
        text_document
           The text document to add

        notebook_uri
           If set, indicates that this text document represents a cell in a notebook
           document
        """
        doc_uri = text_document.uri

        self._text_documents[doc_uri] = self._create_text_document(
            doc_uri,
            source=text_document.text,
            version=text_document.version,
            language_id=text_document.language_id,
        )

        if notebook_uri:
            self._cell_in_notebook[doc_uri] = notebook_uri

    def remove_notebook_document(self, params: types.DidChangeNotebookDocumentParams):
        notebook_uri = params.notebook_document.uri
        self._notebook_documents.pop(notebook_uri, None)

        for cell_document in params.cell_text_documents:
            self.remove_text_document(cell_document.uri)

    def remove_text_document(self, doc_uri: str):
        self._text_documents.pop(doc_uri, None)
        self._cell_in_notebook.pop(doc_uri, None)

    def remove_folder(self, folder_uri: str):
        self._folders.pop(folder_uri, None)
        try:
            del self._folders[folder_uri]
        except KeyError:
            pass

    @property
    def root_path(self):
        return self._root_path

    @property
    def root_uri(self):
        return self._root_uri

    def update_notebook_document(self, params: types.DidChangeNotebookDocumentParams):
        uri = params.notebook_document.uri
        notebook = self._notebook_documents[uri]
        notebook.version = params.notebook_document.version

        if params.change.metadata:
            notebook.metadata = params.change.metadata

        cell_changes = params.change.cells
        if cell_changes is None:
            return

        # Process changes to any cell metadata.
        nb_cells = {cell.document: cell for cell in notebook.cells}
        for new_data in cell_changes.data or []:
            nb_cell = nb_cells.get(new_data.document)
            if nb_cell is None:
                logger.warning(
                    "Ignoring metadata for '%s': not in notebook.", new_data.document
                )
                continue

            nb_cell.kind = new_data.kind
            nb_cell.metadata = new_data.metadata
            nb_cell.execution_summary = new_data.execution_summary

        # Process changes to the notebook's structure
        structure = cell_changes.structure
        if structure:
            cells = notebook.cells
            new_cells = structure.array.cells or []

            # Re-order the cells
            before = cells[: structure.array.start]
            after = cells[(structure.array.start + structure.array.delete_count) :]
            notebook.cells = [*before, *new_cells, *after]

            for new_cell in structure.did_open or []:
                self.put_text_document(new_cell, notebook_uri=uri)

            for removed_cell in structure.did_close or []:
                self.remove_text_document(removed_cell.uri)

        # Process changes to the text content of existing cells.
        for text in cell_changes.text_content or []:
            for change in text.changes:
                self.update_text_document(text.document, change)

    def update_text_document(
        self,
        text_doc: types.VersionedTextDocumentIdentifier,
        change: types.TextDocumentContentChangeEvent,
    ):
        doc_uri = text_doc.uri
        self._text_documents[doc_uri].apply_change(change)
        self._text_documents[doc_uri].version = text_doc.version

    def get_document(self, *args, **kwargs):
        warnings.warn(
            "'workspace.get_document' has been deprecated, use "
            "'workspace.get_text_document' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.get_text_document(*args, **kwargs)

    def remove_document(self, *args, **kwargs):
        warnings.warn(
            "'workspace.remove_document' has been deprecated, use "
            "'workspace.remove_text_document' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.remove_text_document(*args, **kwargs)

    def put_document(self, *args, **kwargs):
        warnings.warn(
            "'workspace.put_document' has been deprecated, use "
            "'workspace.put_text_document' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.put_text_document(*args, **kwargs)

    def update_document(self, *args, **kwargs):
        warnings.warn(
            "'workspace.update_document' has been deprecated, use "
            "'workspace.update_text_document' instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.update_text_document(*args, **kwargs)
