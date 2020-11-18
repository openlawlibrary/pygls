
import unittest
from typing import List, Optional

from pygls.lsp.methods import SELECTION_RANGE
from pygls.lsp.types import (Position, Range, SelectionRange, SelectionRangeOptions,
                             SelectionRangeParams, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestSelectionRange(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            SELECTION_RANGE,
            SelectionRangeOptions(),
        )
        def f(params: SelectionRangeParams) -> Optional[List[SelectionRange]]:
            if params.text_document.uri == 'file://return.list':
                root = SelectionRange(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=10, character=10),
                    ),
                )

                inner_range = SelectionRange(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                    parent=root,
                )

                return [root, inner_range]
            else:
                return None

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.selection_range_provider

    def test_selection_range_return_list(self):
        response = self.client.lsp.send_request(
            SELECTION_RANGE,
            SelectionRangeParams(
                query='query',
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                positions=[Position(line=0, character=0)],
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        root = response[0]
        assert root['range']['start']['line'] == 0
        assert root['range']['start']['character'] == 0
        assert root['range']['end']['line'] == 10
        assert root['range']['end']['character'] == 10
        assert not hasattr(root, 'parent')

        assert response[1]['range']['start']['line'] == 0
        assert response[1]['range']['start']['character'] == 0
        assert response[1]['range']['end']['line'] == 1
        assert response[1]['range']['end']['character'] == 1
        assert response[1]['parent'] == root

    def test_selection_range_return_none(self):
        response = self.client.lsp.send_request(
            SELECTION_RANGE,
            SelectionRangeParams(
                query='query',
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                positions=[Position(line=0, character=0)],
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None


if __name__ == '__main__':
    unittest.main()

