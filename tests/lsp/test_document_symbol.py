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

from typing import List, Union

from lsprotocol.types import TEXT_DOCUMENT_DOCUMENT_SYMBOL
from lsprotocol.types import (
    DocumentSymbol,
    DocumentSymbolOptions,
    DocumentSymbolParams,
    Location,
    Position,
    Range,
    SymbolInformation,
    SymbolKind,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_DOCUMENT_SYMBOL,
            DocumentSymbolOptions(),
        )
        def f(
            params: DocumentSymbolParams,
        ) -> Union[List[SymbolInformation], List[DocumentSymbol]]:
            symbol_info = SymbolInformation(
                name="symbol",
                kind=SymbolKind.Namespace,
                location=Location(
                    uri="uri",
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                ),
                container_name="container",
                deprecated=False,
            )

            document_symbol_inner = DocumentSymbol(
                name="inner_symbol",
                kind=SymbolKind.Number,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
            )

            document_symbol = DocumentSymbol(
                name="symbol",
                kind=SymbolKind.Object,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=10),
                ),
                selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=10),
                ),
                detail="detail",
                children=[document_symbol_inner],
                deprecated=True,
            )

            return {  # type: ignore
                "file://return.symbol_information_list": [symbol_info],
                "file://return.document_symbol_list": [document_symbol],
            }.get(params.text_document.uri, None)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.document_symbol_provider


@ConfiguredLS.decorate()
def test_document_symbol_return_symbol_information_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DOCUMENT_SYMBOL,
        DocumentSymbolParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.symbol_information_list"
            ),
        ),
    ).result()

    assert response

    assert response[0].name == "symbol"
    assert response[0].kind == SymbolKind.Namespace
    assert response[0].location.uri == "uri"
    assert response[0].location.range.start.line == 0
    assert response[0].location.range.start.character == 0
    assert response[0].location.range.end.line == 1
    assert response[0].location.range.end.character == 1
    assert response[0].container_name == "container"
    assert not response[0].deprecated


@ConfiguredLS.decorate()
def test_document_symbol_return_document_symbol_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DOCUMENT_SYMBOL,
        DocumentSymbolParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.document_symbol_list"
            ),
        ),
    ).result()

    assert response

    assert response[0].name == "symbol"
    assert response[0].kind == SymbolKind.Object
    assert response[0].range.start.line == 0
    assert response[0].range.start.character == 0
    assert response[0].range.end.line == 10
    assert response[0].range.end.character == 10
    assert response[0].selection_range.start.line == 0
    assert response[0].selection_range.start.character == 0
    assert response[0].selection_range.end.line == 10
    assert response[0].selection_range.end.character == 10
    assert response[0].detail == "detail"
    assert response[0].deprecated

    assert response[0].children[0].name == "inner_symbol"
    assert response[0].children[0].kind == SymbolKind.Number
    assert response[0].children[0].range.start.line == 0
    assert response[0].children[0].range.start.character == 0
    assert response[0].children[0].range.end.line == 1
    assert response[0].children[0].range.end.character == 1
    range = response[0].children[0].selection_range
    assert range.start.line == 0
    assert range.start.character == 0
    assert range.end.line == 1
    assert range.end.character == 1

    assert response[0].children[0].children is None
