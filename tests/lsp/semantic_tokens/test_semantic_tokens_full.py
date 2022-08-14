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
from typing import Optional, Union

from lsprotocol.types import (
    TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
)
from lsprotocol.types import (
    SemanticTokens,
    SemanticTokensLegend,
    SemanticTokensParams,
    SemanticTokensPartialResult,
    TextDocumentIdentifier,
)

from ...conftest import ClientServer

SemanticTokenReturnType = Optional[
    Union[
        SemanticTokensPartialResult,
        Optional[SemanticTokens]
    ]
]


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
            SemanticTokensLegend(
                token_types=["keyword", "operator"],
                token_modifiers=["readonly"]
            ),
        )
        def f(
            params: SemanticTokensParams,
        ) -> SemanticTokenReturnType:
            if params.text_document.uri == "file://return.tokens":
                return SemanticTokens(data=[0, 0, 3, 0, 0])


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    provider = capabilities.semantic_tokens_provider
    assert provider.full
    assert provider.legend.token_types == [
        "keyword",
        "operator",
    ]
    assert provider.legend.token_modifiers == [
        "readonly"
    ]


@ConfiguredLS.decorate()
def test_semantic_tokens_full_return_tokens(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
        SemanticTokensParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.tokens")
        ),
    ).result()

    assert response

    assert response.data == [0, 0, 3, 0, 0]


@ConfiguredLS.decorate()
def test_semantic_tokens_full_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL,
        SemanticTokensParams(
            text_document=TextDocumentIdentifier(uri="file://return.none")
        ),
    ).result()

    assert response is None
