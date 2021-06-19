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

from pygls.lsp.methods import DOCUMENT_HIGHLIGHT
from pygls.lsp.types import (DocumentHighlight, DocumentHighlightKind, DocumentHighlightOptions,
                             DocumentHighlightParams, Position, Range, TextDocumentIdentifier)

from ..conftest import CALL_TIMEOUT, ClientServer


class TestDocumentHighlight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
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

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

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
        assert 'kind' not in response[0]

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
