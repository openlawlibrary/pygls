
import unittest
from typing import List, Optional

from pygls.lsp.methods import DOCUMENT_HIGHLIGHT
from pygls.lsp.types import (DocumentHighlight, DocumentHighlightKind, DocumentHighlightOptions,
                             DocumentHighlightParams, Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentHighlight(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            DOCUMENT_HIGHLIGHT,
            DocumentHighlightOptions(),
        )
        def f(params: DocumentHighlightParams) -> Optional[List[DocumentHighlight]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    DocumentHighlight(
                       range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                    ),
                    DocumentHighlight(
                       range=Range(
                            start=Position(line=1, character=1),
                            end=Position(line=2, character=2),
                        ),
                        kind=DocumentHighlightKind.Write,
                    ),
                ]
            else:
                return None

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.document_highlight_provider

    def test_document_highlight_return_list(self):
        response = self.client.lsp.send_request(
            DOCUMENT_HIGHLIGHT,
            DocumentHighlightParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1
        assert response[0]['kind'] == DocumentHighlightKind.Text

        assert response[1]['range']['start']['line'] == 1
        assert response[1]['range']['start']['character'] == 1
        assert response[1]['range']['end']['line'] == 2
        assert response[1]['range']['end']['character'] == 2
        assert response[1]['kind'] == DocumentHighlightKind.Write

    def test_document_highlight_return_none(self):
        response = self.client.lsp.send_request(
            DOCUMENT_HIGHLIGHT,
            DocumentHighlightParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

