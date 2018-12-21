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
import re
from typing import List

from .types import (NumType, Position, TextDocumentContentChangeEvent,
                    TextDocumentItem, WorkspaceFolder)
from .uris import to_fs_path, urlparse

# TODO: this is not the best e.g. we capture numbers
RE_END_WORD = re.compile('^[A-Za-z_0-9]*')
RE_START_WORD = re.compile('[A-Za-z_0-9]*$')

log = logging.getLogger(__name__)


class Document(object):

    def __init__(self, uri, source=None, version=None, local=True,):
        self.uri = uri
        self.version = version
        self.path = to_fs_path(uri)
        self.filename = os.path.basename(self.path)

        self._local = local
        self._source = source

    def __str__(self):
        return str(self.uri)

    def apply_change(self, change: TextDocumentContentChangeEvent) -> None:
        """Apply a change to the document."""
        text = change.text
        change_range = change.range

        if not change_range:
            # The whole file has changed
            self._source = text
            return

        start_line = change_range.start.line
        start_col = change_range.start.character
        end_line = change_range.end.line
        end_col = change_range.end.character

        # Check for an edit occuring at the very end of the file
        if start_line == len(self.lines):
            self._source = self.source + text
            return

        new = io.StringIO()

        # Iterate over the existing document until we hit the edit range,
        # at which point we write the new text, then loop until we hit
        # the end of the range and continue writing.
        for i, line in enumerate(self.lines):
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

    @property
    def lines(self) -> List[str]:
        return self.source.splitlines(True)

    def offset_at_position(self, position: Position) -> int:
        """Return the byte-offset pointed at by the given position."""
        return position.character + len(''.join(self.lines[:position.line]))

    @property
    def source(self) -> str:
        if self._source is None:
            with io.open(self.path, 'r', encoding='utf-8') as f:
                return f.read()
        return self._source

    def word_at_position(self, position: Position) -> str:
        """
        Get the word under the cursor returning the start and end positions.
        """
        if position.line >= len(self.lines):
            return ''

        line = self.lines[position.line]
        i = position.character
        # Split word in two
        start = line[:i]
        end = line[i:]

        # Take end of start and start of end to find word
        # These are guaranteed to match, even if they match the empty string
        m_start = RE_START_WORD.findall(start)
        m_end = RE_END_WORD.findall(end)

        return m_start[0] + m_end[-1]


class Workspace(object):

    def __init__(self, root_uri, lsp):
        self._root_uri = root_uri
        self._lsp = lsp
        self._root_uri_scheme = urlparse(self._root_uri)[0]
        self._root_path = to_fs_path(self._root_uri)
        self._folders = {}
        self._docs = {}

    def _create_document(self,
                         doc_uri: str,
                         source: str = None,
                         version: NumType = None) -> Document:
        return Document(doc_uri, source=source, version=version)

    def add_folder(self, folder: WorkspaceFolder):
        self._folders[folder.uri] = folder

    @property
    def documents(self):
        return self._docs

    @property
    def folders(self):
        return self._folders

    def get_document(self, doc_uri: str) -> Document:
        """
        Return a managed document if-present,
        else create one pointing at disk.

        See https://github.com/Microsoft/language-server-protocol/issues/177
        """
        return self._docs.get(doc_uri) or self._create_document(doc_uri)

    def is_local(self):
        return (self._root_uri_scheme == '' or
                self._root_uri_scheme == 'file') and \
            os.path.exists(self._root_path)

    def put_document(self, text_document: TextDocumentItem):
        doc_uri = text_document.uri

        self._docs[doc_uri] = self._create_document(
            doc_uri,
            source=text_document.text,
            version=text_document.version
        )

    def remove_document(self, doc_uri: str):
        self._docs.pop(doc_uri)

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

    def update_document(self,
                        text_doc: TextDocumentItem,
                        change: TextDocumentContentChangeEvent):
        doc_uri = text_doc.uri
        self._docs[doc_uri].apply_change(change)
        self._docs[doc_uri].version = text_doc.version
