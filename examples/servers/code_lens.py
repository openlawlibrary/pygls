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
"""This implements the :lsp:`textDocument/codeLens` and :lsp:`codeLens/resolve` requests.

`In VSCode <https://code.visualstudio.com/blogs/2017/02/12/code-lens-roundup>`__
a code lens is shown as "ghost text" above some line of actual code in your document.
These lenses are typically used to show some contextual information (e.g. number of
references) or provide easy access to some command (e.g. run this test).

This server scans the document for incomplete sums e.g. ``1 + 1 =`` and returns a code
lens object which, when clicked, will call the ``codeLens.evaluateSum`` command to fill
in the answer.
Note that while we could have easily compute the ``command`` field of the code lens up
front, this example demonstrates how the ``codeLens/resolve`` can be used to defer this
computation until it is actually necessary.
"""

import logging
import re

import attrs
from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer

ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=(?=\s*$)")
server = LanguageServer("code-lens-server", "v1")


@server.feature(types.TEXT_DOCUMENT_CODE_LENS)
def code_lens(params: types.CodeLensParams):
    """Return a list of code lens to insert into the given document.

    This method will read the whole document and identify each sum in the document and
    tell the language client to insert a code lens at each location.
    """
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    lines = document.lines
    for idx, line in enumerate(lines):
        match = ADDITION.match(line)
        if match is not None:
            range_ = types.Range(
                start=types.Position(line=idx, character=0),
                end=types.Position(line=idx, character=len(line) - 1),
            )

            left = int(match.group(1))
            right = int(match.group(2))

            code_lens = types.CodeLens(
                range=range_,
                data={
                    "left": left,
                    "right": right,
                    "uri": document_uri,
                },
            )
            items.append(code_lens)

    return items


@attrs.define
class EvaluateSumArgs:
    """Represents the arguments to pass to the ``codeLens.evaluateSum`` command"""

    uri: str
    """The uri of the document to edit"""

    left: int
    """The left argument to ``+``"""

    right: int
    """The right argument to ``+``"""

    line: int
    """The line number to edit"""


@server.feature(types.CODE_LENS_RESOLVE)
def code_lens_resolve(ls: LanguageServer, item: types.CodeLens):
    """Resolve the ``command`` field of the given code lens.

    Using the ``data`` that was attached to the code lens item created in the function
    above, this prepares an invocation of the ``evaluateSum`` command below.
    """
    logging.info("Resolving code lens: %s", item)

    left = item.data["left"]
    right = item.data["right"]
    uri = item.data["uri"]

    args = EvaluateSumArgs(
        uri=uri,
        left=left,
        right=right,
        line=item.range.start.line,
    )

    item.command = types.Command(
        title=f"Evaluate {left} + {right}",
        command="codeLens.evaluateSum",
        arguments=[args],
    )
    return item


@server.command("codeLens.evaluateSum")
def evaluate_sum(ls: LanguageServer, args: EvaluateSumArgs):
    logging.info("arguments: %s", args)

    document = ls.workspace.get_text_document(args.uri)
    line = document.lines[args.line]

    # Compute the edit that will update the document with the result.
    answer = args.left + args.right
    edit = types.TextDocumentEdit(
        text_document=types.OptionalVersionedTextDocumentIdentifier(
            uri=args.uri,
            version=document.version,
        ),
        edits=[
            types.TextEdit(
                new_text=f"{line.strip()} {answer}\n",
                range=types.Range(
                    start=types.Position(line=args.line, character=0),
                    end=types.Position(line=args.line + 1, character=0),
                ),
            )
        ],
    )

    # Apply the edit.
    ls.workspace_apply_edit(
        types.ApplyWorkspaceEditParams(
            edit=types.WorkspaceEdit(document_changes=[edit]),
        ),
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
