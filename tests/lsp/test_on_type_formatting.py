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

from lsprotocol.types import TEXT_DOCUMENT_ON_TYPE_FORMATTING
from lsprotocol.types import (
    DocumentOnTypeFormattingOptions,
    DocumentOnTypeFormattingParams,
    FormattingOptions,
    Position,
    Range,
    TextDocumentIdentifier,
    TextEdit,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_ON_TYPE_FORMATTING,
            DocumentOnTypeFormattingOptions(
                first_trigger_character=":",
                more_trigger_character=[",", "."],
            ),
        )
        def f(
            params: DocumentOnTypeFormattingParams
        ) -> Optional[List[TextEdit]]:
            if params.text_document.uri == "file://return.list":
                return [
                    TextEdit(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        new_text="text",
                    )
                ]
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.document_on_type_formatting_provider
    assert (
        capabilities
        .document_on_type_formatting_provider
        .first_trigger_character
        == ":"
    )
    assert (
        capabilities
        .document_on_type_formatting_provider
        .more_trigger_character
        == [",", "."]
    )


@ConfiguredLS.decorate()
def test_on_type_formatting_return_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_ON_TYPE_FORMATTING,
        DocumentOnTypeFormattingParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            position=Position(line=0, character=0),
            ch=":",
            options=FormattingOptions(
                tab_size=2,
                insert_spaces=True,
                trim_trailing_whitespace=True,
                insert_final_newline=True,
                trim_final_newlines=True,
            ),
        ),
    ).result()

    assert response

    assert response[0].new_text == "text"
    assert response[0].range.start.line == 0
    assert response[0].range.start.character == 0
    assert response[0].range.end.line == 1
    assert response[0].range.end.character == 1


@ConfiguredLS.decorate()
def test_on_type_formatting_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_ON_TYPE_FORMATTING,
        DocumentOnTypeFormattingParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
            ch=":",
            options=FormattingOptions(
                tab_size=2,
                insert_spaces=True,
                trim_trailing_whitespace=True,
                insert_final_newline=True,
                trim_final_newlines=True,
            ),
        ),
    ).result()

    assert response is None
