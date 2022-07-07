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
from pygls.lsp.methods import COMPLETION
from pygls.lsp.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    Position,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            COMPLETION,
            CompletionOptions(
                trigger_characters=[","],
                all_commit_characters=[":"],
                resolve_provider=True,
            ),
        )
        def f(params: CompletionParams) -> CompletionList:
            return CompletionList(
                is_incomplete=False,
                items=[
                    CompletionItem(
                        label="test1",
                        kind=CompletionItemKind.Method,
                        preselect=True,
                    ),
                ],
            )


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.completion_provider
    assert capabilities.completion_provider.trigger_characters == [","]
    assert capabilities.completion_provider.all_commit_characters == [":"]
    assert capabilities.completion_provider.resolve_provider is True


@ConfiguredLS.decorate()
def test_completions(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        COMPLETION,
        CompletionParams(
            text_document=TextDocumentIdentifier(uri="file://test.test"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert not response["isIncomplete"]
    assert response["items"][0]["label"] == "test1"
    assert response["items"][0]["kind"] == CompletionItemKind.Method
    assert response["items"][0]["preselect"]
    assert "deprecated" not in response["items"][0]
    assert "tags" not in response["items"][0]
    assert "detail" not in response["items"][0]
    assert "documentation" not in response["items"][0]
    assert "sort_text" not in response["items"][0]
    assert "filter_text" not in response["items"][0]
    assert "insert_text" not in response["items"][0]
    assert "insert_text_format" not in response["items"][0]
    assert "insert_text_mode" not in response["items"][0]
    assert "text_edit" not in response["items"][0]
    assert "additional_text_edits" not in response["items"][0]
    assert "commit_characters" not in response["items"][0]
    assert "command" not in response["items"][0]
    assert "data" not in response["items"][0]
