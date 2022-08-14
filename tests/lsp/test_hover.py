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

from lsprotocol.types import TEXT_DOCUMENT_HOVER
from lsprotocol.types import (
    Hover,
    HoverOptions,
    HoverParams,
    MarkedString_Type1,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentIdentifier,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_HOVER,
            HoverOptions(),
        )
        def f(params: HoverParams) -> Optional[Hover]:
            range = Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=1),
            )

            return {
                "file://return.marked_string": Hover(
                    range=range,
                    contents=MarkedString_Type1(
                        language="language",
                        value="value",
                    ),
                ),
                "file://return.marked_string_list": Hover(
                    range=range,
                    contents=[
                        MarkedString_Type1(
                            language="language",
                            value="value",
                        ),
                        "str type",
                    ],
                ),
                "file://return.markup_content": Hover(
                    range=range,
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown, value="value"),
                ),
            }.get(params.text_document.uri, None)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.hover_provider


@ConfiguredLS.decorate()
def test_hover_return_marked_string(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_HOVER,
        HoverParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.marked_string"),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.contents.language == "language"
    assert response.contents.value == "value"

    assert response.range.start.line == 0
    assert response.range.start.character == 0
    assert response.range.end.line == 1
    assert response.range.end.character == 1


@ConfiguredLS.decorate()
def test_hover_return_marked_string_list(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_HOVER,
        HoverParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.marked_string_list"
            ),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.contents[0].language == "language"
    assert response.contents[0].value == "value"
    assert response.contents[1] == "str type"

    assert response.range.start.line == 0
    assert response.range.start.character == 0
    assert response.range.end.line == 1
    assert response.range.end.character == 1


@ConfiguredLS.decorate()
def test_hover_return_markup_content(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_HOVER,
        HoverParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.markup_content"
            ),
            position=Position(line=0, character=0),
        ),
    ).result()

    assert response

    assert response.contents.kind == MarkupKind.Markdown
    assert response.contents.value == "value"

    assert response.range.start.line == 0
    assert response.range.start.character == 0
    assert response.range.end.line == 1
    assert response.range.end.character == 1
