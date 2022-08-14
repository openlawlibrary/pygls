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

from lsprotocol.types import TEXT_DOCUMENT_FOLDING_RANGE
from lsprotocol.types import (
    FoldingRange,
    FoldingRangeKind,
    FoldingRangeOptions,
    FoldingRangeParams,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_FOLDING_RANGE,
            FoldingRangeOptions(),
        )
        def f(params: FoldingRangeParams) -> Optional[List[FoldingRange]]:
            if params.text_document.uri == "file://return.list":
                return [
                    FoldingRange(
                        start_line=0,
                        end_line=0,
                        start_character=1,
                        end_character=1,
                        kind=FoldingRangeKind.Comment,
                    ),
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.folding_range_provider


@ConfiguredLS.decorate()
def test_folding_range_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_FOLDING_RANGE,
        FoldingRangeParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
        ),
    ).result()

    assert response

    assert response[0].start_line == 0
    assert response[0].end_line == 0
    assert response[0].start_character == 1
    assert response[0].end_character == 1
    assert response[0].kind == FoldingRangeKind.Comment


@ConfiguredLS.decorate()
def test_folding_range_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_FOLDING_RANGE,
        FoldingRangeParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
        ),
    ).result()

    assert response is None
