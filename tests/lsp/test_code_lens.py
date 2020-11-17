
import unittest
from typing import List, Optional

from pygls.lsp.methods import CODE_LENS
from pygls.lsp.types import (CodeLens, CodeLensOptions, CodeLensParams, Command, Position, Range,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestCodeLens(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
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

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.lsp.capabilities

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

