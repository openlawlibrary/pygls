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

from lsprotocol.types import TEXT_DOCUMENT_SELECTION_RANGE
from lsprotocol.types import (
    Position,
    Range,
    SelectionRange,
    SelectionRangeOptions,
    SelectionRangeParams,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_SELECTION_RANGE,
            SelectionRangeOptions(),
        )
        def f(params: SelectionRangeParams) -> Optional[List[SelectionRange]]:
            if params.text_document.uri == "file://return.list":
                root = SelectionRange(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=10, character=10),
                    ),
                )

                inner_range = SelectionRange(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                    parent=root,
                )

                return [root, inner_range]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.selection_range_provider


@ConfiguredLS.decorate()
def test_selection_range_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SELECTION_RANGE,
        SelectionRangeParams(
            # query="query",
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            positions=[Position(line=0, character=0)],
        ),
    ).result()

    assert response

    root = response[0]
    assert root.range.start.line == 0
    assert root.range.start.character == 0
    assert root.range.end.line == 10
    assert root.range.end.character == 10
    assert root.parent is None

    assert response[1].range.start.line == 0
    assert response[1].range.start.character == 0
    assert response[1].range.end.line == 1
    assert response[1].range.end.character == 1
    assert response[1].parent == root


@ConfiguredLS.decorate()
def test_selection_range_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_SELECTION_RANGE,
        SelectionRangeParams(
            # query="query",
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            positions=[Position(line=0, character=0)],
        ),
    ).result()

    assert response is None
