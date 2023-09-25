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
import re
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_ACTION,
    CodeAction,
    CodeActionKind,
    CodeActionOptions,
    CodeActionParams,
    Position,
    Range,
    TextEdit,
    WorkspaceEdit,
)


ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=\s*$")
server = LanguageServer("code-action-server", "v0.1")


@server.feature(
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionOptions(code_action_kinds=[CodeActionKind.QuickFix]),
)
def code_actions(params: CodeActionParams):
    items = []
    document_uri = params.text_document.uri
    document = server.workspace.get_document(document_uri)

    start_line = params.range.start.line
    end_line = params.range.end.line

    lines = document.lines[start_line : end_line + 1]
    for idx, line in enumerate(lines):
        match = ADDITION.match(line)
        if match is not None:
            range_ = Range(
                start=Position(line=start_line + idx, character=0),
                end=Position(line=start_line + idx, character=len(line) - 1),
            )

            left = int(match.group(1))
            right = int(match.group(2))
            answer = left + right

            text_edit = TextEdit(range=range_, new_text=f"{line.strip()} {answer}!")

            action = CodeAction(
                title=f"Evaluate '{match.group(0)}'",
                kind=CodeActionKind.QuickFix,
                edit=WorkspaceEdit(changes={document_uri: [text_edit]}),
            )
            items.append(action)

    return items


if __name__ == "__main__":
    server.start_io()
