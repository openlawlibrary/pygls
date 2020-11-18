import unittest

from pygls.lsp.methods import COMPLETION
from pygls.lsp.types import (CompletionItem, CompletionItemKind, CompletionList, CompletionOptions,
                             CompletionParams, Position, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCompletions(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            COMPLETION,
            CompletionOptions(trigger_characters=[','], all_commit_characters=[':'], resolve_provider=True)
        )
        def f(params: CompletionParams) -> CompletionList:
            return CompletionList(
                is_incomplete=False,
                items=[
                    CompletionItem(
                        label='test1',
                        kind=CompletionItemKind.Method
                    ),
                ]
            )

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.lsp.capabilities

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
        assert response['items'][0]['preselect'] == False
        assert response['items'][0]['deprecated'] == False



if __name__ == '__main__':
    unittest.main()
