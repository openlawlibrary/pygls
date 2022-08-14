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

from lsprotocol.types import TEXT_DOCUMENT_DOCUMENT_LINK
from lsprotocol.types import (
    DocumentLink,
    DocumentLinkOptions,
    DocumentLinkParams,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_DOCUMENT_LINK,
            DocumentLinkOptions(resolve_provider=True),
        )
        def f(params: DocumentLinkParams) -> Optional[List[DocumentLink]]:
            if params.text_document.uri == "file://return.list":
                return [
                    DocumentLink(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        target="target",
                        tooltip="tooltip",
                        data="data",
                    ),
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.document_link_provider
    assert capabilities.document_link_provider.resolve_provider


@ConfiguredLS.decorate()
def test_document_link_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DOCUMENT_LINK,
        DocumentLinkParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
        ),
    ).result()

    assert response

    assert response[0].range.start.line == 0
    assert response[0].range.start.character == 0
    assert response[0].range.end.line == 1
    assert response[0].range.end.character == 1
    assert response[0].target == "target"
    assert response[0].tooltip == "tooltip"
    assert response[0].data == "data"


@ConfiguredLS.decorate()
def test_document_link_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DOCUMENT_LINK,
        DocumentLinkParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
        ),
    ).result()

    assert response is None
