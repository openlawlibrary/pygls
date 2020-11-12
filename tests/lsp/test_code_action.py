import unittest
from typing import List, Optional, Union

from pygls.lsp.methods import CODE_ACTION
from pygls.lsp.types import (CodeAction, CodeActionContext, CodeActionKind, CodeActionOptions,
                             CodeActionParams, Command, Diagnostic, Position, Range,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCodeAction(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
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

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.lsp.capabilities

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
