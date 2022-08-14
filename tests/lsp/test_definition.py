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

from lsprotocol.types import TEXT_DOCUMENT_DEFINITION
from lsprotocol.types import (
    DefinitionOptions,
    DefinitionParams,
    Location,
    LocationLink,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_DEFINITION,
            DefinitionOptions(),
        )
        def f(
            params: DefinitionParams,
        ) -> Optional[Union[Location, List[Location], List[LocationLink]]]:
            location = Location(
                uri="uri",
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
            )

            location_link = LocationLink(
                target_uri="uri",
                target_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                target_selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=2, character=2),
                ),
                origin_selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=3, character=3),
                ),
            )

            return {  # type: ignore
                "file://return.location": location,
                "file://return.location_list": [location],
                "file://return.location_link_list": [location_link],
            }.get(params.text_document.uri, None)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.definition_provider is not None


@ConfiguredLS.decorate()
def test_definition_return_location(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DEFINITION,
        DefinitionParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.location"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response.uri == "uri"

    assert response.range.start.line == 0
    assert response.range.start.character == 0
    assert response.range.end.line == 1
    assert response.range.end.character == 1


@ConfiguredLS.decorate()
def test_definition_return_location_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DEFINITION,
        DefinitionParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.location_list"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response[0].uri == "uri"

    assert response[0].range.start.line == 0
    assert response[0].range.start.character == 0
    assert response[0].range.end.line == 1
    assert response[0].range.end.character == 1


@ConfiguredLS.decorate()
def test_definition_return_location_link_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DEFINITION,
        DefinitionParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.location_link_list"
            ),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response[0].target_uri == "uri"

    assert response[0].target_range.start.line == 0
    assert response[0].target_range.start.character == 0
    assert response[0].target_range.end.line == 1
    assert response[0].target_range.end.character == 1

    assert response[0].target_selection_range.start.line == 0
    assert response[0].target_selection_range.start.character == 0
    assert response[0].target_selection_range.end.line == 2
    assert response[0].target_selection_range.end.character == 2

    assert response[0].origin_selection_range.start.line == 0
    assert response[0].origin_selection_range.start.character == 0
    assert response[0].origin_selection_range.end.line == 3
    assert response[0].origin_selection_range.end.character == 3


@ConfiguredLS.decorate()
def test_definition_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_DEFINITION,
        DefinitionParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response is None
