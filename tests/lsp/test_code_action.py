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
from typing import List, Optional, Union

from lsprotocol.types import TEXT_DOCUMENT_CODE_ACTION
from lsprotocol.types import (
    CodeAction,
    CodeActionContext,
    CodeActionKind,
    CodeActionOptions,
    CodeActionParams,
    Command,
    Diagnostic,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_CODE_ACTION,
            CodeActionOptions(code_action_kinds=[CodeActionKind.Refactor])
        )
        def f(
            params: CodeActionParams
        ) -> Optional[List[Union[Command, CodeAction]]]:
            if params.text_document.uri == "file://return.list":
                return [
                    CodeAction(title="action1"),
                    CodeAction(title="action2", kind=CodeActionKind.Refactor),
                    Command(
                        title="cmd1", command="cmd1",
                        arguments=[1, "two"]
                    ),
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.code_action_provider
    assert capabilities.code_action_provider.code_action_kinds == [
        CodeActionKind.Refactor
    ]


@ConfiguredLS.decorate()
def test_code_action_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_CODE_ACTION,
        CodeActionParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=1),
            ),
            context=CodeActionContext(
                diagnostics=[
                    Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        message="diagnostic",
                    )
                ],
                only=[CodeActionKind.Refactor],
            ),
        ),
    ).result()

    assert response[0].title == "action1"
    assert response[1].title == "action2"
    assert response[1].kind == CodeActionKind.Refactor.value
    assert response[2].title == "cmd1"
    assert response[2].command == "cmd1"
    assert response[2].arguments == [1, "two"]


@ConfiguredLS.decorate()
def test_code_action_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_CODE_ACTION,
        CodeActionParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=1),
            ),
            context=CodeActionContext(
                diagnostics=[
                    Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        message="diagnostic",
                    )
                ],
                only=[CodeActionKind.Refactor],
            ),
        ),
    ).result()

    assert response is None
