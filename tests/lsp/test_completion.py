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
from lsprotocol.types import TEXT_DOCUMENT_COMPLETION
from lsprotocol.types import (
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
            TEXT_DOCUMENT_COMPLETION,
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
        TEXT_DOCUMENT_COMPLETION,
        CompletionParams(
            text_document=TextDocumentIdentifier(uri="file://test.test"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert not response.is_incomplete
    assert response.items[0].label == "test1"
    assert response.items[0].kind == CompletionItemKind.Method
    assert response.items[0].preselect
    assert response.items[0].deprecated is None
    assert response.items[0].tags is None
    assert response.items[0].detail is None
    assert response.items[0].documentation is None
    assert response.items[0].sort_text is None
    assert response.items[0].filter_text is None
    assert response.items[0].insert_text is None
    assert response.items[0].insert_text_format is None
    assert response.items[0].insert_text_mode is None
    assert response.items[0].text_edit is None
    assert response.items[0].additional_text_edits is None
    assert response.items[0].commit_characters is None
    assert response.items[0].command is None
    assert response.items[0].data is None
