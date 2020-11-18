
import unittest
from typing import Optional

from pygls.lsp.methods import HOVER
from pygls.lsp.types import (Hover, HoverOptions, HoverParams, MarkedString, MarkupContent,
                             MarkupKind, Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestHover(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(
            HOVER,
            HoverOptions(),
        )
        def f(params: HoverParams) -> Optional[Hover]:
            range = Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=1),
            )

            return {
                'file://return.marked_string': Hover(
                    range=range,
                    contents=MarkedString(
                        language='language',
                        value='value',
                    ),
                ),
                'file://return.marked_string_list': Hover(
                    range=range,
                    contents=[
                        MarkedString(
                            language='language',
                            value='value',
                        ),
                        'str type'
                    ],
                ),
                'file://return.markup_content': Hover(
                    range=range,
                    contents=MarkupContent(
                        kind=MarkupKind.Markdown,
                        value='value'
                    ),
                ),
            }.get(params.text_document.uri, None)

        self.client_server.start()

    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.hover_provider

    def test_hover_return_marked_string(self):
        response = self.client.lsp.send_request(
            HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri='file://return.marked_string'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['contents']['language'] == 'language'
        assert response['contents']['value'] == 'value'

        assert response['range']['start']['line'] == 0
        assert response['range']['start']['character'] == 0
        assert response['range']['end']['line'] == 1
        assert response['range']['end']['character'] == 1

    def test_hover_return_marked_string_list(self):
        response = self.client.lsp.send_request(
            HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri='file://return.marked_string_list'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['contents'][0]['language'] == 'language'
        assert response['contents'][0]['value'] == 'value'
        assert response['contents'][1] == 'str type'

        assert response['range']['start']['line'] == 0
        assert response['range']['start']['character'] == 0
        assert response['range']['end']['line'] == 1
        assert response['range']['end']['character'] == 1

    def test_hover_return_markup_content(self):
        response = self.client.lsp.send_request(
            HOVER,
            HoverParams(
                text_document=TextDocumentIdentifier(uri='file://return.markup_content'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['contents']['kind'] == MarkupKind.Markdown
        assert response['contents']['value'] == 'value'

        assert response['range']['start']['line'] == 0
        assert response['range']['start']['character'] == 0
        assert response['range']['end']['line'] == 1
        assert response['range']['end']['character'] == 1



if __name__ == '__main__':
    unittest.main()

