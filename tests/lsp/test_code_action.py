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

from pygls.lsp.methods import CODE_ACTION
from pygls.lsp.types import (CodeAction, CodeActionContext, CodeActionKind, CodeActionOptions,
                             CodeActionParams, Command, Diagnostic, Position, Range,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCodeAction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            CODE_ACTION,
            CodeActionOptions(code_action_kinds=[CodeActionKind.Refactor])
        )
        def f(params: CodeActionParams) -> Optional[List[Union[Command, CodeAction]]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    CodeAction(title='action1'),
                    CodeAction(title='action2', kind=CodeActionKind.Refactor),
                    Command(title='cmd1', command='cmd1', arguments=[1, 'two']),
                ]
            else:
                return None

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.code_action_provider
        assert capabilities.code_action_provider.code_action_kinds == [CodeActionKind.Refactor]

    def test_code_action_return_list(self):
        response = self.client.lsp.send_request(
            CODE_ACTION,
            CodeActionParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                context=CodeActionContext(
                    diagnostics=[
                        Diagnostic(
                            range=Range(
                                start=Position(line=0, character=0),
                                end=Position(line=1, character=1),
                            ),
                            message='diagnostic'
                        )
                    ],
                    only=[CodeActionKind.Refactor]
                )
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response[0]['title'] == 'action1'
        assert response[1]['title'] == 'action2'
        assert response[1]['kind'] == CodeActionKind.Refactor
        assert response[2]['title'] == 'cmd1'
        assert response[2]['command'] == 'cmd1'
        assert response[2]['arguments'] == [1, 'two']

    def test_code_action_return_none(self):
        response = self.client.lsp.send_request(
            CODE_ACTION,
            CodeActionParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                context=CodeActionContext(
                    diagnostics=[
                        Diagnostic(
                            range=Range(
                                start=Position(line=0, character=0),
                                end=Position(line=1, character=1),
                            ),
                            message='diagnostic',
                        )
                    ],
                    only=[CodeActionKind.Refactor],
                )
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()
