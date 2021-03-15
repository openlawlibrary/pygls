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
from typing import List, Optional, Union

from pygls.lsp.methods import IMPLEMENTATION
from pygls.lsp.types import (ImplementationOptions, ImplementationParams, Location, LocationLink,
                             Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestImplementation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            IMPLEMENTATION,
            ImplementationOptions(),
        )
        def f(params: ImplementationParams) -> Optional[Union[Location, List[Location], List[LocationLink]]]:
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

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.implementation_provider

    def test_type_definition_return_location(self):
        response = self.client.lsp.send_request(
            IMPLEMENTATION,
            ImplementationParams(
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
            IMPLEMENTATION,
            ImplementationParams(
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
            IMPLEMENTATION,
            ImplementationParams(
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
            IMPLEMENTATION,
            ImplementationParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

