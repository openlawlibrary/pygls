
import unittest
from typing import List

from pygls.lsp.methods import DOCUMENT_COLOR
from pygls.lsp.types import (Color, ColorInformation, DocumentColorOptions, DocumentColorParams,
                             Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentColor(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            DOCUMENT_COLOR,
            DocumentColorOptions(),
        )
        def f(params: DocumentColorParams) -> List[ColorInformation]:
            return [
                ColorInformation(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                    color=Color(red=0.5, green=0.5, blue=0.5, alpha=0.5),
                )
            ]

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.color_provider

    def test_document_color(self):
        response = self.client.lsp.send_request(
            DOCUMENT_COLOR,
            DocumentColorParams(text_document=TextDocumentIdentifier(uri='file://return.list')),
        ).result(timeout=CALL_TIMEOUT)

        assert response
        assert response[0]['color']['red'] == 0.5
        assert response[0]['color']['green'] == 0.5
        assert response[0]['color']['blue'] == 0.5
        assert response[0]['color']['alpha'] == 0.5

        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1



if __name__ == '__main__':
    unittest.main()

