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
from typing import List

from pygls.lsp.methods import DOCUMENT_COLOR
from pygls.lsp.types import (Color, ColorInformation, DocumentColorOptions, DocumentColorParams,
                             Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentColor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
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

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

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

