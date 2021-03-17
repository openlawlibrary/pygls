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

from pygls.lsp.methods import FOLDING_RANGE
from pygls.lsp.types import (FoldingRange, FoldingRangeKind, FoldingRangeOptions,
                             FoldingRangeParams, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestFoldingRange(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            FOLDING_RANGE,
            FoldingRangeOptions(),
        )
        def f(params: FoldingRangeParams) -> Optional[List[FoldingRange]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    FoldingRange(
                        start_line=0,
                        end_line=0,
                        start_character=1,
                        end_character=1,
                        kind=FoldingRangeKind.Comment,
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

        assert capabilities.folding_range_provider

    def test_folding_range_return_list(self):
        response = self.client.lsp.send_request(
            FOLDING_RANGE,
            FoldingRangeParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['startLine'] == 0
        assert response[0]['endLine'] == 0
        assert response[0]['startCharacter'] == 1
        assert response[0]['endCharacter'] == 1
        assert response[0]['kind'] == FoldingRangeKind.Comment

    def test_folding_range_return_none(self):
        response = self.client.lsp.send_request(
            FOLDING_RANGE,
            FoldingRangeParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()

