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

from lsprotocol.types import TEXT_DOCUMENT_REFERENCES
from lsprotocol.types import (
    Location,
    Position,
    Range,
    ReferenceContext,
    ReferenceOptions,
    ReferenceParams,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_REFERENCES,
            ReferenceOptions(),
        )
        def f(params: ReferenceParams) -> Optional[List[Location]]:
            if params.text_document.uri == "file://return.list":
                return [
                    Location(
                        uri="uri",
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                    ),
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.references_provider


@ConfiguredLS.decorate()
def test_references_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_REFERENCES,
        ReferenceParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            position=Position(line=0, character=0),
            context=ReferenceContext(
                include_declaration=True,
            ),
        ),
    ).result()

    assert response

    assert response[0].uri == "uri"

    assert response[0].range.start.line == 0
    assert response[0].range.start.character == 0
    assert response[0].range.end.line == 1
    assert response[0].range.end.character == 1


@ConfiguredLS.decorate()
def test_references_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_REFERENCES,
        ReferenceParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
            context=ReferenceContext(
                include_declaration=True,
            ),
        ),
    ).result()

    assert response is None
