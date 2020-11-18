
import unittest
from typing import List, Optional

from pygls.lsp.methods import FOLDING_RANGE
from pygls.lsp.types import (FoldingRange, FoldingRangeKind, FoldingRangeOptions,
                             FoldingRangeParams, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestFoldingRange(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
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

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.lsp.capabilities

        assert capabilities.folding_range_provider

    def test_folding_range_return_list(self):
        response = self.client.lsp.send_request(
            FOLDING_RANGE,
            FoldingRangeParams(
                query='query',
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
                query='query',
                text_document=TextDocumentIdentifier(uri='file://return.none'),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()

