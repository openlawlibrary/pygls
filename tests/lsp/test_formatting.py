
import unittest
from typing import List, Optional

from pygls.lsp.methods import FORMATTING
from pygls.lsp.types import (DocumentFormattingOptions, DocumentFormattingParams,
                             FormattingOptions, Position, Range, TextDocumentIdentifier, TextEdit)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentFormatting(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            FORMATTING,
            DocumentFormattingOptions(),
        )
        def f(params: DocumentFormattingParams) -> Optional[List[TextEdit]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    TextEdit(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        new_text='text',
                    )
                ]
            else:
                return None

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.document_formatting_provider

    def test_document_formatting_return_list(self):
        response = self.client.lsp.send_request(
            FORMATTING,
            DocumentFormattingParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                options=FormattingOptions(
                    tab_size=2,
                    insert_spaces=True,
                    trim_trailing_whitespace=True,
                    insert_final_newline=True,
                    trim_final_newlines=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['newText'] == 'text'
        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1

    def test_document_formatting_return_none(self):
        response = self.client.lsp.send_request(
            FORMATTING,
            DocumentFormattingParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                options=FormattingOptions(
                    tab_size=2,
                    insert_spaces=True,
                    trim_trailing_whitespace=True,
                    insert_final_newline=True,
                    trim_final_newlines=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

