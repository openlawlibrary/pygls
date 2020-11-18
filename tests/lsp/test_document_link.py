
import unittest
from typing import List, Optional

from pygls.lsp.methods import DOCUMENT_LINK
from pygls.lsp.types import (DocumentLink, DocumentLinkOptions, DocumentLinkParams, Position,
                             Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentLink(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            DOCUMENT_LINK,
            DocumentLinkOptions(resolve_provider=True),
        )
        def f(params: DocumentLinkParams) -> Optional[List[DocumentLink]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    DocumentLink(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        target='target',
                        tooltip='tooltip',
                        data='data',
                    ),
                ]
            else:
                return None

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.lsp.capabilities

        assert capabilities.document_link_provider
        assert capabilities.document_link_provider.resolve_provider == True

    def test_document_link_return_list(self):
        response = self.client.lsp.send_request(
            DOCUMENT_LINK,
            DocumentLinkParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1
        assert response[0]['target'] == 'target'
        assert response[0]['tooltip'] == 'tooltip'
        assert response[0]['data'] == 'data'

    def test_document_link_return_none(self):
        response = self.client.lsp.send_request(
            DOCUMENT_LINK,
            DocumentLinkParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

