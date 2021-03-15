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
from typing import Optional

from pygls.lsp.methods import HOVER
from pygls.lsp.types import (Hover, HoverOptions, HoverParams, MarkedString, MarkupContent,
                             MarkupKind, Position, Range, TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestHover(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
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

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

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

