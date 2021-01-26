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

from pygls.lsp.methods import COMPLETION
from pygls.lsp.types import (CompletionItem, CompletionItemKind, CompletionList, CompletionOptions,
                             CompletionParams, Position, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCompletions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            COMPLETION,
            CompletionOptions(trigger_characters=[','], all_commit_characters=[':'], resolve_provider=True)
        )
        def f(params: CompletionParams) -> CompletionList:
            return CompletionList(
                is_incomplete=False,
                items=[
                    CompletionItem(
                        label='test1',
                        kind=CompletionItemKind.Method,
                        preselect=True,
                    ),
                ]
            )

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.completion_provider
        assert capabilities.completion_provider.trigger_characters == [',']
        assert capabilities.completion_provider.all_commit_characters == [':']
        assert capabilities.completion_provider.resolve_provider is True

    def test_completions(self):
        response = self.client.lsp.send_request(
            COMPLETION,
            CompletionParams(
                text_document=TextDocumentIdentifier(uri='file://test.test'),
                position=Position(line=0, character=0)
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response['isIncomplete'] == False
        assert response['items'][0]['label'] == 'test1'
        assert response['items'][0]['kind'] == CompletionItemKind.Method
        assert response['items'][0]['preselect'] == True
        assert 'deprecated' not in response['items'][0]



if __name__ == '__main__':
    unittest.main()
