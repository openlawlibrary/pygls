
import unittest
from typing import List, Optional, Union

from pygls.lsp.methods import TYPE_DEFINITION
from pygls.lsp.types import (Location, LocationLink, Position, Range, TextDocumentIdentifier,
                             TypeDefinitionOptions, TypeDefinitionParams)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestTypeDefinition(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            TYPE_DEFINITION,
            TypeDefinitionOptions(),
        )
        def f(params: TypeDefinitionParams) -> Optional[Union[Location, List[Location], List[LocationLink]]]:
            location = Location(
                uri='uri',
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
            )

            location_link = LocationLink(
                target_uri='uri',
                target_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                target_selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=2, character=2),
                ),
                origin_selection_range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=3, character=3),
                ),
            )

            return {    # type: ignore
                'file://return.location': location,
                'file://return.location_list': [location],
                'file://return.location_link_list': [location_link],
            }.get(params.text_document.uri, None)

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.type_definition_provider

    def test_type_definition_return_location(self):
        response = self.client.lsp.send_request(
            TYPE_DEFINITION,
            TypeDefinitionParams(
                text_document=TextDocumentIdentifier(uri='file://return.location'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response['uri'] == 'uri'

        assert response['range']['start']['line'] == 0
        assert response['range']['start']['character'] == 0
        assert response['range']['end']['line'] == 1
        assert response['range']['end']['character'] == 1

    def test_type_definition_return_location_list(self):
        response = self.client.lsp.send_request(
            TYPE_DEFINITION,
            TypeDefinitionParams(
                text_document=TextDocumentIdentifier(uri='file://return.location_list'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response[0]['uri'] == 'uri'

        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1

    def test_type_definition_return_location_link_list(self):
        response = self.client.lsp.send_request(
            TYPE_DEFINITION,
            TypeDefinitionParams(
                text_document=TextDocumentIdentifier(uri='file://return.location_link_list'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response[0]['targetUri'] == 'uri'

        assert response[0]['targetRange']['start']['line'] == 0
        assert response[0]['targetRange']['start']['character'] == 0
        assert response[0]['targetRange']['end']['line'] == 1
        assert response[0]['targetRange']['end']['character'] == 1

        assert response[0]['targetSelectionRange']['start']['line'] == 0
        assert response[0]['targetSelectionRange']['start']['character'] == 0
        assert response[0]['targetSelectionRange']['end']['line'] == 2
        assert response[0]['targetSelectionRange']['end']['character'] == 2

        assert response[0]['originSelectionRange']['start']['line'] == 0
        assert response[0]['originSelectionRange']['start']['character'] == 0
        assert response[0]['originSelectionRange']['end']['line'] == 3
        assert response[0]['originSelectionRange']['end']['character'] == 3

    def test_type_definition_return_none(self):
        response = self.client.lsp.send_request(
            TYPE_DEFINITION,
            TypeDefinitionParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

