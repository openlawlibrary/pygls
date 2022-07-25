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

from typing import List, Optional

from pygls.lsp.methods import DOCUMENT_HIGHLIGHT
from pygls.lsp.types import (
    DocumentHighlight,
    DocumentHighlightKind,
    DocumentHighlightOptions,
    DocumentHighlightParams,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            DOCUMENT_HIGHLIGHT,
            DocumentHighlightOptions(),
        )
        def f(
            params: DocumentHighlightParams
        ) -> Optional[List[DocumentHighlight]]:
            if params.text_document.uri == "file://return.list":
                return [
                    DocumentHighlight(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                    ),
                    DocumentHighlight(
                        range=Range(
                            start=Position(line=1, character=1),
                            end=Position(line=2, character=2),
                        ),
                        kind=DocumentHighlightKind.Write,
                    ),
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.document_highlight_provider


@ConfiguredLS.decorate()
def test_document_highlight_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        DOCUMENT_HIGHLIGHT,
        DocumentHighlightParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response[0]["range"]["start"]["line"] == 0
    assert response[0]["range"]["start"]["character"] == 0
    assert response[0]["range"]["end"]["line"] == 1
    assert response[0]["range"]["end"]["character"] == 1
    assert "kind" not in response[0]

    assert response[1]["range"]["start"]["line"] == 1
    assert response[1]["range"]["start"]["character"] == 1
    assert response[1]["range"]["end"]["line"] == 2
    assert response[1]["range"]["end"]["character"] == 2
    assert response[1]["kind"] == DocumentHighlightKind.Write


@ConfiguredLS.decorate()
def test_document_highlight_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        DOCUMENT_HIGHLIGHT,
        DocumentHighlightParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response is None
