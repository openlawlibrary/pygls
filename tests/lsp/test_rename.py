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

from pygls.lsp.methods import RENAME
from pygls.lsp.types import (CreateFile, CreateFileOptions, DeleteFile, DeleteFileOptions,
                             OptionalVersionedTextDocumentIdentifier, Position, Range, RenameFile,
                             RenameFileOptions, RenameOptions, RenameParams, TextDocumentEdit,
                             TextDocumentIdentifier, TextEdit, WorkspaceEdit)
from pygls.server import LanguageServer

from ..conftest import CALL_TIMEOUT, ClientServer


class TestRename(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server

        @cls.server.feature(
            RENAME,
            RenameOptions(prepare_provider=True),
        )
        def f(params: RenameParams) -> Optional[WorkspaceEdit]:
            if params.text_document.uri == 'file://return.workspace_edit':
                return WorkspaceEdit(
                    changes={
                        'uri1': [
                            TextEdit(
                                range=Range(
                                    start=Position(line=0, character=0),
                                    end=Position(line=1, character=1),
                                ),
                                new_text='text1',
                            ),
                            TextEdit(
                                range=Range(
                                    start=Position(line=1, character=1),
                                    end=Position(line=2, character=2),
                                ),
                                new_text='text2',
                            ),
                        ],
                    },
                    document_changes=[
                        TextDocumentEdit(
                            text_document=OptionalVersionedTextDocumentIdentifier(
                                uri='uri',
                                version=3,
                            ),
                            edits=[
                                TextEdit(
                                    range=Range(
                                        start=Position(line=2, character=2),
                                        end=Position(line=3, character=3),
                                    ),
                                    new_text='text3',
                                ),
                            ]
                        ),
                        CreateFile(
                            uri='create file',
                            options=CreateFileOptions(
                                overwrite=True,
                                ignore_if_exists=True,
                            ),
                        ),
                        RenameFile(
                            old_uri='rename old uri',
                            new_uri='rename new uri',
                            options=RenameFileOptions(
                                overwrite=True,
                                ignore_if_exists =True,
                            )
                        ),
                        DeleteFile(
                            uri='delete file',
                            options=DeleteFileOptions(
                                recursive=True,
                                ignore_if_exists=True,
                            ),
                        ),
                    ]
                )
            else:
                return None

        cls.client_server.start()


    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.rename_provider
        assert capabilities.rename_provider.prepare_provider == True

    def test_rename_return_workspace_edit(self):
        response = self.client.lsp.send_request(
            RENAME,
            RenameParams(
                text_document=TextDocumentIdentifier(uri='file://return.workspace_edit'),
                position=Position(line=0, character=0),
                new_name='new name',
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response

        assert response['changes']['uri1'][0]['newText'] == 'text1'
        assert response['changes']['uri1'][0]['range']['start']['line'] == 0
        assert response['changes']['uri1'][0]['range']['start']['character'] == 0
        assert response['changes']['uri1'][0]['range']['end']['line'] == 1
        assert response['changes']['uri1'][0]['range']['end']['character'] == 1

        assert response['changes']['uri1'][1]['newText'] == 'text2'
        assert response['changes']['uri1'][1]['range']['start']['line'] == 1
        assert response['changes']['uri1'][1]['range']['start']['character'] == 1
        assert response['changes']['uri1'][1]['range']['end']['line'] == 2
        assert response['changes']['uri1'][1]['range']['end']['character'] == 2

        assert response['documentChanges'][0]['textDocument']['uri'] == 'uri'
        assert response['documentChanges'][0]['textDocument']['version'] == 3
        assert response['documentChanges'][0]['edits'][0]['newText'] == 'text3'
        assert response['documentChanges'][0]['edits'][0]['range']['start']['line'] == 2
        assert response['documentChanges'][0]['edits'][0]['range']['start']['character'] == 2
        assert response['documentChanges'][0]['edits'][0]['range']['end']['line'] == 3
        assert response['documentChanges'][0]['edits'][0]['range']['end']['character'] == 3

        assert response['documentChanges'][1]['uri'] == 'create file'
        assert response['documentChanges'][1]['options']['ignoreIfExists'] == True
        assert response['documentChanges'][1]['options']['overwrite'] == True

        assert response['documentChanges'][2]['newUri'] == 'rename new uri'
        assert response['documentChanges'][2]['oldUri'] == 'rename old uri'
        assert response['documentChanges'][2]['options']['ignoreIfExists'] == True
        assert response['documentChanges'][2]['options']['overwrite'] == True

        assert response['documentChanges'][3]['uri'] == 'delete file'
        assert response['documentChanges'][3]['options']['ignoreIfExists'] == True
        assert response['documentChanges'][3]['options']['recursive'] == True

    def test_rename_return_none(self):
        response = self.client.lsp.send_request(
            RENAME,
            RenameParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                position=Position(line=0, character=0),
                new_name='new name',
            ),
        ).result(timeout=CALL_TIMEOUT)

        assert response is None



if __name__ == '__main__':
    unittest.main()

