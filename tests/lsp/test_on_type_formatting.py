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

from pygls.lsp.methods import ON_TYPE_FORMATTING
from pygls.lsp.types import (DocumentOnTypeFormattingOptions, DocumentOnTypeFormattingParams,
                             FormattingOptions, Position, Range, TextDocumentIdentifier, TextEdit)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestOnTypeFormatting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            ON_TYPE_FORMATTING,
            DocumentOnTypeFormattingOptions(
                first_trigger_character=':',
                more_trigger_character=[',', '.'],
            ),
        )
        def f(params: DocumentOnTypeFormattingParams) -> Optional[List[TextEdit]]:
            if params.text_document.uri == 'file://return.list':
                return [
                    TextEdit(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=1, character=1),
                        ),
                        new_text='text',
                    )
                ]
            else:
                return None

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.document_on_type_formatting_provider
        assert capabilities.document_on_type_formatting_provider.first_trigger_character == ':'
        assert capabilities.document_on_type_formatting_provider.more_trigger_character == [',', '.']

    def test_on_type_formatting_return_list(self):
        response = self.client.lsp.send_request(
            ON_TYPE_FORMATTING,
            DocumentOnTypeFormattingParams(
                text_document=TextDocumentIdentifier(uri='file://return.list'),
                position=Position(line=0, character=0),
                ch=':',
                options=FormattingOptions(
                    tab_size=2,
                    insert_spaces=True,
                    trim_trailing_whitespace=True,
                    insert_final_newline=True,
                    trim_final_newlines=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response[0]['newText'] == 'text'
        assert response[0]['range']['start']['line'] == 0
        assert response[0]['range']['start']['character'] == 0
        assert response[0]['range']['end']['line'] == 1
        assert response[0]['range']['end']['character'] == 1

    def test_on_type_formatting_return_none(self):
        response = self.client.lsp.send_request(
            ON_TYPE_FORMATTING,
            DocumentOnTypeFormattingParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
                ch=':',
                options=FormattingOptions(
                    tab_size=2,
                    insert_spaces=True,
                    trim_trailing_whitespace=True,
                    insert_final_newline=True,
                    trim_final_newlines=True,
                ),
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

