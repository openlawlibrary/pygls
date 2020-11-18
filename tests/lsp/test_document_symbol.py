
import unittest
from typing import List, Union

from pygls.lsp.methods import DOCUMENT_SYMBOL
from pygls.lsp.types import (DocumentSymbol, DocumentSymbolOptions, DocumentSymbolParams, Location,
                             Position, Range, SymbolInformation, SymbolKind,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentSymbol(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            DOCUMENT_SYMBOL,
            DocumentSymbolOptions(),
        )
        def f(params: DocumentSymbolParams) -> Union[List[SymbolInformation], List[DocumentSymbol]]:
            symbol_info = SymbolInformation(
                name='symbol',
                kind=SymbolKind.Namespace,
                location=Location(
                    uri='uri',
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                ),
                container_name='container',
                deprecated=False,
            )

            document_symbol_inner = DocumentSymbol(
                name='inner_symbol',
                kind=SymbolKind.Number,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
            )

            document_symbol = DocumentSymbol(
                name='symbol',
                kind=SymbolKind.Object,
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=10),
                ),
                selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=10, character=10),
                ),
                detail='detail',
                children=[document_symbol_inner],
                deprecated=True,
            )

            return {
                'file://return.symbol_information_list': [symbol_info],
                'file://return.document_symbol_list': [document_symbol],
            }.get(params.text_document.uri, None)

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.document_symbol_provider

    def test_document_symbol_return_symbol_information_list(self):
        response = self.client.lsp.send_request(
            DOCUMENT_SYMBOL,
            DocumentSymbolParams(
                text_document=TextDocumentIdentifier(uri='file://return.symbol_information_list'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['name'] == 'symbol'
        assert response[0]['kind'] == SymbolKind.Namespace
        assert response[0]['location']['uri'] == 'uri'
        assert response[0]['location']['range']['start']['line'] == 0
        assert response[0]['location']['range']['start']['character'] == 0
        assert response[0]['location']['range']['end']['line'] == 1
        assert response[0]['location']['range']['end']['character'] == 1
        assert response[0]['containerName'] == 'container'
        assert response[0]['deprecated'] == False

    def test_document_symbol_return_document_symbol_list(self):
        response = self.client.lsp.send_request(
            DOCUMENT_SYMBOL,
            DocumentSymbolParams(
                text_document=TextDocumentIdentifier(uri='file://return.document_symbol_list'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['name'] == 'symbol'
        assert response[0]['kind'] == SymbolKind.Object
        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 10
        assert response[0]['range']['end']['character'] == 10
        assert response[0]['selectionRange']['start']['line'] == 0
        assert response[0]['selectionRange']['start']['character'] == 0
        assert response[0]['selectionRange']['end']['line'] == 10
        assert response[0]['selectionRange']['end']['character'] == 10
        assert response[0]['detail'] == 'detail'
        assert response[0]['deprecated'] == True

        assert response[0]['children'][0]['name'] == 'inner_symbol'
        assert response[0]['children'][0]['kind'] == SymbolKind.Number
        assert response[0]['children'][0]['range']['start']['line'] == 0
        assert response[0]['children'][0]['range']['start']['character'] == 0
        assert response[0]['children'][0]['range']['end']['line'] == 1
        assert response[0]['children'][0]['range']['end']['character'] == 1
        assert response[0]['children'][0]['selectionRange']['start']['line'] == 0
        assert response[0]['children'][0]['selectionRange']['start']['character'] == 0
        assert response[0]['children'][0]['selectionRange']['end']['line'] == 1
        assert response[0]['children'][0]['selectionRange']['end']['character'] == 1

        assert not hasattr(response[0]['children'][0], 'children')




if __name__ == '__main__':
    unittest.main()

