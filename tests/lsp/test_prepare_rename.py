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

from lsprotocol.types import TEXT_DOCUMENT_PREPARE_RENAME
from lsprotocol.types import (
    Position,
    PrepareRenameResult,
    PrepareRenameResult_Type1,
    PrepareRenameParams,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(TEXT_DOCUMENT_PREPARE_RENAME)
        def f(
            params: PrepareRenameParams
        ) -> Optional[Union[Range, PrepareRenameResult]]:
            return {  # type: ignore
                "file://return.range": Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                "file://return.prepare_rename": PrepareRenameResult_Type1(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                    placeholder="placeholder",
                ),
            }.get(params.text_document.uri, None)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    pass


@ConfiguredLS.decorate()
def test_prepare_rename_return_range(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_PREPARE_RENAME,
        PrepareRenameParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.range"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.start.line == 0
    assert response.start.character == 0
    assert response.end.line == 1
    assert response.end.character == 1


@ConfiguredLS.decorate()
def test_prepare_rename_return_prepare_rename(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_PREPARE_RENAME,
        PrepareRenameParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.prepare_rename"
            ),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.range.start.line == 0
    assert response.range.start.character == 0
    assert response.range.end.line == 1
    assert response.range.end.character == 1
    assert response.placeholder == "placeholder"


@ConfiguredLS.decorate()
def test_prepare_rename_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_PREPARE_RENAME,
        PrepareRenameParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response is None
