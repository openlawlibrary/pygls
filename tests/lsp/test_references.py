
import unittest
from typing import List, Optional

from pygls.lsp.methods import REFERENCES
from pygls.lsp.types import (Location, Position, Range, ReferenceContext, ReferenceOptions,
                             ReferenceParams, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestReferences(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            REFERENCES,
            ReferenceOptions(),
        )
        def f(params: ReferenceParams) -> Optional[List[Location]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    Location(
                        uri='uri',
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                    ),
                ]
            else:
                return None

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.references_provider

    def test_references_return_list(self):
        response = self.client.lsp.send_request(
            REFERENCES,
            ReferenceParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                position=Position(line=0, character=0),
                context=ReferenceContext(
                    include_declaration=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['uri'] == 'uri'

        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1

    def test_references_return_none(self):
        response = self.client.lsp.send_request(
            REFERENCES,
            ReferenceParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
                context=ReferenceContext(
                    include_declaration=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

