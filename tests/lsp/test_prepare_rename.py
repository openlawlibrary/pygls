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
from typing import Optional, Union

from pygls.lsp.methods import PREPARE_RENAME
from pygls.lsp.types import (Position, PrepareRename, PrepareRenameParams, Range,
                             TextDocumentIdentifier)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestRepareRename(unittest.TestCase):
    def setUp(self):
        self.client_server = ClientServer()
        self.client, self.server = self.client_server

        @self.server.feature(PREPARE_RENAME)
        def f(params: PrepareRenameParams) -> Optional[Union[Range, PrepareRename]]:
            return {    # type: ignore
                'file://return.range': Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                'file://return.prepare_rename': PrepareRename(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=1, character=1),
                    ),
                    placeholder='placeholder',
                ),
            }.get(params.text_document.uri, None)

        self.client_server.start()


    def tearDown(self):
        self.client_server.stop()

    def test_capabilities(self):
        pass

    def test_prepare_rename_return_range(self):
        response = self.client.lsp.send_request(
            PREPARE_RENAME,
            PrepareRenameParams(
                text_document=TextDocumentIdentifier(uri='file://return.range'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['start']['line'] == 0
        assert response['start']['character'] == 0
        assert response['end']['line'] == 1
        assert response['end']['character'] == 1

    def test_prepare_rename_return_prepare_rename(self):
        response = self.client.lsp.send_request(
            PREPARE_RENAME,
            PrepareRenameParams(
                text_document=TextDocumentIdentifier(uri='file://return.prepare_rename'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['range']['start']['line'] == 0
        assert response['range']['start']['character'] == 0
        assert response['range']['end']['line'] == 1
        assert response['range']['end']['character'] == 1
        assert response['placeholder'] == 'placeholder'

    def test_prepare_rename_return_none(self):
        response = self.client.lsp.send_request(
            PREPARE_RENAME,
            PrepareRenameParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

