
import unittest
from typing import List

from pygls.lsp.methods import COLOR_PRESENTATION
from pygls.lsp.types import (Color, ColorPresentation, ColorPresentationParams, Position, Range,
                             TextDocumentIdentifier, TextEdit)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestColorPresentation(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(COLOR_PRESENTATION)
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

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

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

