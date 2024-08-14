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

from typing import Optional

from lsprotocol.types import TEXT_DOCUMENT_LINKED_EDITING_RANGE
from lsprotocol.types import (
    LinkedEditingRangeOptions,
    LinkedEditingRangeParams,
    LinkedEditingRanges,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_LINKED_EDITING_RANGE,
            LinkedEditingRangeOptions(),
        )
        def f(params: LinkedEditingRangeParams) -> Optional[LinkedEditingRanges]:
            if params.text_document.uri == "file://return.ranges":
                return LinkedEditingRanges(
                    ranges=[
                        Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        Range(
                            start=Position(line=1, character=1),
                            end=Position(line=2, character=2),
                        ),
                    ],
                    word_pattern="pattern",
                )
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.linked_editing_range_provider


@ConfiguredLS.decorate()
def test_linked_editing_ranges_return_ranges(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        TEXT_DOCUMENT_LINKED_EDITING_RANGE,
        LinkedEditingRangeParams(
            text_document=TextDocumentIdentifier(uri="file://return.ranges"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.ranges[0].start.line == 0
    assert response.ranges[0].start.character == 0
    assert response.ranges[0].end.line == 1
    assert response.ranges[0].end.character == 1
    assert response.ranges[1].start.line == 1
    assert response.ranges[1].start.character == 1
    assert response.ranges[1].end.line == 2
    assert response.ranges[1].end.character == 2
    assert response.word_pattern == "pattern"


@ConfiguredLS.decorate()
def test_linked_editing_ranges_return_none(client_server):
    client, _ = client_server
    response = client.protocol.send_request(
        TEXT_DOCUMENT_LINKED_EDITING_RANGE,
        LinkedEditingRangeParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response is None
