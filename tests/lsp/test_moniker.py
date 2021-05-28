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
from typing import List, Optional

from pygls.lsp.methods import TEXT_DOCUMENT_MONIKER
from pygls.lsp.types import (Moniker, MonikerKind, MonikerOptions, MonikerParams, Position,
                             TextDocumentIdentifier, UniquenessLevel)

from ..conftest import CALL_TIMEOUT, ClientServer


class TestMoniker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            TEXT_DOCUMENT_MONIKER,
            MonikerOptions(),
        )
        def f(params: MonikerParams) -> Optional[List[Moniker]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    Moniker(
                        scheme='test_scheme',
                        identifier='test_identifier',
                        unique=UniquenessLevel.Global,
                        kind=MonikerKind.Local,
                    ),
                ]
            else:
                return None

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.moniker_provider

    def test_moniker_return_list(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_MONIKER,
            MonikerParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                position=Position(line=0, character=0),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['scheme'] == 'test_scheme'
        assert response[0]['identifier'] == 'test_identifier'
        assert response[0]['unique'] == 'global'
        assert response[0]['kind'] == 'local'

    def test_references_return_none(self):
        response = self.client.lsp.send_request(
            TEXT_DOCUMENT_MONIKER,
            MonikerParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()

