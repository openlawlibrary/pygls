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
import logging
import re

from lsprotocol import types

from pygls import IS_WASM
from pygls.lsp.server import LanguageServer

ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=(?=\s*$)")
server = LanguageServer("code-action-server", "v1")


@server.feature(
    types.TEXT_DOCUMENT_CODE_ACTION,
    types.CodeActionOptions(code_action_kinds=[types.CodeActionKind.QuickFix]),
)
def code_actions(params: types.CodeActionParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_text_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    for idx, line in enumerate(lines):
        match = ADDITION.match(line)
        if match is not None:
            range_ = types.Range(
                start=types.Position(line=start_line + idx, character=0),
                end=types.Position(line=start_line + idx, character=len(line) - 1),
            )

            left = int(match.group(1))
            right = int(match.group(2))
            answer = left + right

            text_edit = types.TextEdit(
                range=range_, new_text=f"{line.strip()} {answer}!"
            )

            action = types.CodeAction(
                title=f"Evaluate '{match.group(0)}'",
                kind=types.CodeActionKind.QuickFix,
                edit=types.WorkspaceEdit(changes={document_uri: [text_edit]}),
            )
            items.append(action)

    return items


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")

    if IS_WASM:
        server.start_io()
    else:
        import asyncio

        asyncio.run(server.start_io())
