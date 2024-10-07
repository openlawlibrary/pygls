############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
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
"""This implements :lsp:`textDocument/rename` and :lsp:`textDocument/prepareRename`

The ``textDocument/rename`` method should return a collection of edits the client should
perform in order to correctly rename all occurances of the given symbol.

The ``textDocument/prepareRename`` method is used by the client to check that it
actually makes sense to rename the given symbol, giving the server chance to reject the
operation as invalid.

.. note::

   This server's rename implementation is no different to a naive find and replace,
   a real server would have to check to make sure it only renames symbols in the
   relevant scope.
"""

import logging
import re
from typing import List

from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument

ARGUMENT = re.compile(r"(?P<name>\w+): (?P<type>\w+)")
FUNCTION = re.compile(r"^fn ([a-z]\w+)\(")
TYPE = re.compile(r"^type ([A-Z]\w+)\(")


class RenameLanguageServer(LanguageServer):
    """Language server demonstrating symbol renaming."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = {}

    def parse(self, doc: TextDocument):
        typedefs = {}
        funcs = {}

        for linum, line in enumerate(doc.lines):
            if (match := TYPE.match(line)) is not None:
                name = match.group(1)
                start_char = match.start() + line.find(name)

                typedefs[name] = types.Range(
                    start=types.Position(line=linum, character=start_char),
                    end=types.Position(line=linum, character=start_char + len(name)),
                )

            elif (match := FUNCTION.match(line)) is not None:
                name = match.group(1)
                start_char = match.start() + line.find(name)

                funcs[name] = types.Range(
                    start=types.Position(line=linum, character=start_char),
                    end=types.Position(line=linum, character=start_char + len(name)),
                )

        self.index[doc.uri] = {
            "types": typedefs,
            "functions": funcs,
        }
        logging.info("Index: %s", self.index)


server = RenameLanguageServer("rename-server", "v1")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: RenameLanguageServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is opened"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: RenameLanguageServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is changed"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_RENAME)
def rename(ls: RenameLanguageServer, params: types.RenameParams):
    """Rename the symbol at the given position."""
    logging.debug("%s", params)

    doc = ls.workspace.get_text_document(params.text_document.uri)
    index = ls.index.get(doc.uri)
    if index is None:
        return None

    word = doc.word_at_position(params.position)
    is_object = any([word in index[name] for name in index])
    if not is_object:
        return None

    edits: List[types.TextEdit] = []
    for linum, line in enumerate(doc.lines):
        for match in re.finditer(f"\\b{word}\\b", line):
            edits.append(
                types.TextEdit(
                    new_text=params.new_name,
                    range=types.Range(
                        start=types.Position(line=linum, character=match.start()),
                        end=types.Position(line=linum, character=match.end()),
                    ),
                )
            )

    return types.WorkspaceEdit(changes={params.text_document.uri: edits})


@server.feature(types.TEXT_DOCUMENT_PREPARE_RENAME)
def prepare_rename(ls: RenameLanguageServer, params: types.PrepareRenameParams):
    """Called by the client to determine if renaming the symbol at the given location
    is a valid operation."""
    logging.debug("%s", params)

    doc = ls.workspace.get_text_document(params.text_document.uri)
    index = ls.index.get(doc.uri)
    if index is None:
        return None

    word = doc.word_at_position(params.position)
    is_object = any([word in index[name] for name in index])
    if not is_object:
        return None

    # At this point, we can rename this symbol.
    #
    # For simplicity we can tell the client to use its default behaviour however, it's
    # relatively new to the spec (LSP v3.16+) so a production server should check the
    # client's capabilities before responding in this way
    return types.PrepareRenameDefaultBehavior(default_behavior=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    start_server(server)
