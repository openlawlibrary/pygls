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
import unittest
from typing import List

from pygls.lsp.methods import COLOR_PRESENTATION
from pygls.lsp.types import (Color, ColorPresentation, ColorPresentationParams, Position, Range,
                             TextDocumentIdentifier, TextEdit)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestColorPresentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(COLOR_PRESENTATION)
        def f(params: ColorPresentationParams) -> List[ColorPresentation]:
            return [
                ColorPresentation(
                    label='label1',
                    text_edit=TextEdit(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        new_text='te'
                    ),
                    additional_text_edits=[
                        TextEdit(
                            range=Range(
                                start=Position(line=1, character=1),
                                end=Position(line=2, character=2),
                            ),
                            new_text='ate1'
                        ),
                        TextEdit(
                            range=Range(
                                start=Position(line=2, character=2),
                                end=Position(line=3, character=3),
                            ),
                            new_text='ate2'
                        )
                    ]
                )
            ]

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        '''From specs:

        This request has no special capabilities and registration options since
        it is send as a resolve request for the textDocument/documentColor request.
        '''

    def test_color_presentation(self):
        response = self.client.lsp.send_request(
            COLOR_PRESENTATION,
            ColorPresentationParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                color=Color(red=0.6, green=0.2, blue=0.3, alpha=0.5),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=3, character=3),
                ),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response[0]['label'] == 'label1'
        assert response[0]['textEdit']['newText'] == 'te'

        assert response[0]['textEdit']['range']['start']['line'] == 0
        assert response[0]['textEdit']['range']['start']['character'] == 0
        assert response[0]['textEdit']['range']['end']['line'] == 1
        assert response[0]['textEdit']['range']['end']['character'] == 1

        assert response[0]['additionalTextEdits'][0]['range']['start']['line'] == 1
        assert response[0]['additionalTextEdits'][0]['range']['start']['character'] == 1
        assert response[0]['additionalTextEdits'][0]['range']['end']['line'] == 2
        assert response[0]['additionalTextEdits'][0]['range']['end']['character'] == 2

        assert response[0]['additionalTextEdits'][1]['range']['start']['line'] == 2
        assert response[0]['additionalTextEdits'][1]['range']['start']['character'] == 2
        assert response[0]['additionalTextEdits'][1]['range']['end']['line'] == 3
        assert response[0]['additionalTextEdits'][1]['range']['end']['character'] == 3



if __name__ == '__main__':
    unittest.main()

