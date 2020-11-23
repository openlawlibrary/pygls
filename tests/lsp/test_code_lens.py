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

from pygls.lsp.methods import CODE_LENS
from pygls.lsp.types import (CodeLens, CodeLensOptions, CodeLensParams, Command, Position, Range,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCodeLens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            CODE_LENS,
            CodeLensOptions(resolve_provider=False),
        )
        def f(params: CodeLensParams) -> Optional[List[CodeLens]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    CodeLens(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        command=Command(
                            title='cmd1',
                            command='cmd1',
                        ),
                        data='some data',
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

        assert capabilities.code_lens_provider
        assert capabilities.code_lens_provider.resolve_provider == False

    def test_code_lens_return_list(self):
        response = self.client.lsp.send_request(
            CODE_LENS,
            CodeLensParams(text_document=TextDocumentIdentifier(uri='file://return.list')),
        ).result(timeout=CALL_TIMEOUT)

        assert response[0]['data'] == 'some data'
        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1
        assert response[0]['command']['title'] == 'cmd1'
        assert response[0]['command']['command'] == 'cmd1'

    def test_code_lens_return_none(self):
        response = self.client.lsp.send_request(
            CODE_LENS,
            CodeLensParams(text_document=TextDocumentIdentifier(uri='file://return.none')),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

