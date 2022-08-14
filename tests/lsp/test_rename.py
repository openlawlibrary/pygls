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

from typing import Optional

from lsprotocol.types import TEXT_DOCUMENT_RENAME
from lsprotocol.types import (
    CreateFile,
    CreateFileOptions,
    DeleteFile,
    DeleteFileOptions,
    OptionalVersionedTextDocumentIdentifier,
    Position,
    Range,
    RenameFile,
    RenameFileOptions,
    RenameOptions,
    RenameParams,
    ResourceOperationKind,
    TextDocumentEdit,
    TextDocumentIdentifier,
    TextEdit,
    WorkspaceEdit,
)

from ..conftest import ClientServer

workspace_edit = {
    "changes": {
        "uri1": [
            TextEdit(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=1, character=1),
                ),
                new_text="text1",
            ),
            TextEdit(
                range=Range(
                    start=Position(line=1, character=1),
                    end=Position(line=2, character=2),
                ),
                new_text="text2",
            ),
        ],
    },
    "document_changes": [
        TextDocumentEdit(
            text_document=OptionalVersionedTextDocumentIdentifier(
                uri="uri",
                version=3,
            ),
            edits=[
                TextEdit(
                    range=Range(
                        start=Position(line=2, character=2),
                        end=Position(line=3, character=3),
                    ),
                    new_text="text3",
                ),
            ],
        ),
        CreateFile(
            kind=ResourceOperationKind.Create.value,
            uri="create file",
            options=CreateFileOptions(
                overwrite=True,
                ignore_if_exists=True,
            ),
        ),
        RenameFile(
            kind=ResourceOperationKind.Rename.value,
            old_uri="rename old uri",
            new_uri="rename new uri",
            options=RenameFileOptions(
                overwrite=True,
                ignore_if_exists=True,
            ),
        ),
        DeleteFile(
            kind=ResourceOperationKind.Delete.value,
            uri="delete file",
            options=DeleteFileOptions(
                recursive=True,
                ignore_if_not_exists=True,
            ),
        ),
    ], }


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()

        @self.server.feature(
            TEXT_DOCUMENT_RENAME,
            RenameOptions(prepare_provider=True),
        )
        def f(params: RenameParams) -> Optional[WorkspaceEdit]:
            if params.text_document.uri == "file://return.workspace_edit":
                return WorkspaceEdit(**workspace_edit)
            else:
                return None


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    assert capabilities.rename_provider
    assert capabilities.rename_provider.prepare_provider


@ConfiguredLS.decorate()
def test_rename_return_workspace_edit(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_RENAME,
        RenameParams(
            text_document=TextDocumentIdentifier(
                uri="file://return.workspace_edit"
            ),
            position=Position(line=0, character=0),
            new_name="new name",
        ),
    ).result()

    assert response

    changes = response.changes["uri1"]
    assert changes[0].new_text == "text1"
    assert changes[0].range.start.line == 0
    assert changes[0].range.start.character == 0
    assert changes[0].range.end.line == 1
    assert changes[0].range.end.character == 1

    assert changes[1].new_text == "text2"
    assert changes[1].range.start.line == 1
    assert changes[1].range.start.character == 1
    assert changes[1].range.end.line == 2
    assert changes[1].range.end.character == 2

    changes = response.document_changes
    assert changes[0].text_document.uri == "uri"
    assert changes[0].text_document.version == 3
    assert changes[0].edits[0].new_text == "text3"
    assert changes[0].edits[0].range.start.line == 2
    assert (
        changes[0].edits[0].range.start.character
        == 2
    )
    assert changes[0].edits[0].range.end.line == 3
    assert (
        changes[0].edits[0].range.end.character == 3
    )

    assert changes[1].kind == ResourceOperationKind.Create.value
    assert changes[1].uri == "create file"
    assert changes[1].options.ignore_if_exists
    assert changes[1].options.overwrite

    assert changes[2].kind == ResourceOperationKind.Rename.value
    assert changes[2].new_uri == "rename new uri"
    assert changes[2].old_uri == "rename old uri"
    assert changes[2].options.ignore_if_exists
    assert changes[2].options.overwrite

    assert changes[3].kind == ResourceOperationKind.Delete.value
    assert changes[3].uri == "delete file"
    assert changes[3].options.ignore_if_not_exists
    assert changes[3].options.recursive


@ConfiguredLS.decorate()
def test_rename_return_none(client_server):
    client, _ = client_server
    response = client.lsp.send_request(
        TEXT_DOCUMENT_RENAME,
        RenameParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            position=Position(line=0, character=0),
            new_name="new name",
        ),
    ).result()

    assert response is None
