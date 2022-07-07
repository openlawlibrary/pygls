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

from typing import List

from pygls.lsp.methods import COLOR_PRESENTATION
from pygls.lsp.types import (
    Color,
    ColorPresentation,
    ColorPresentationParams,
    Position,
    Range,
    TextDocumentIdentifier,
    TextEdit,
)

from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(COLOR_PRESENTATION)
        def f(params: ColorPresentationParams) -> List[ColorPresentation]:
            return [
                ColorPresentation(
                    label="label1",
                    text_edit=TextEdit(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        new_text="te",
                    ),
                    additional_text_edits=[
                        TextEdit(
                            range=Range(
                                start=Position(line=1, character=1),
                                end=Position(line=2, character=2),
                            ),
                            new_text="ate1",
                        ),
                        TextEdit(
                            range=Range(
                                start=Position(line=2, character=2),
                                end=Position(line=3, character=3),
                            ),
                            new_text="ate2",
                        ),
                    ],
                )
            ]


@ConfiguredLS.decorate()
def test_capabilities():
    """From specs:

    This request has no special capabilities and registration options since
    it is send as a resolve request for the textDocument/documentColor
    request.
    """


@ConfiguredLS.decorate()
def test_color_presentation(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        COLOR_PRESENTATION,
        ColorPresentationParams(
            text_document=TextDocumentIdentifier(uri="file://return.list"),
            color=Color(red=0.6, green=0.2, blue=0.3, alpha=0.5),
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=3, character=3),
            ),
        ),
    ).result()

    assert response[0]["label"] == "label1"
    assert response[0]["textEdit"]["newText"] == "te"

    assert response[0]["textEdit"]["range"]["start"]["line"] == 0
    assert response[0]["textEdit"]["range"]["start"]["character"] == 0
    assert response[0]["textEdit"]["range"]["end"]["line"] == 1
    assert response[0]["textEdit"]["range"]["end"]["character"] == 1

    range = response[0]["additionalTextEdits"][0]["range"]
    assert range["start"]["line"] == 1
    assert range["start"]["character"] == 1
    assert range["end"]["line"] == 2
    assert range["end"]["character"] == 2

    range = response[0]["additionalTextEdits"][1]["range"]
    assert range["start"]["line"] == 2
    assert range["start"]["character"] == 2
    assert range["end"]["line"] == 3
    assert range["end"]["character"] == 3
