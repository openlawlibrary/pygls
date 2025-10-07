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
from __future__ import annotations

from collections.abc import Sequence
import typing

import pytest
import pytest_asyncio
import cattrs
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture()
async def rename(get_client_for):
    # Indicate to the server that our test client supports `textDocument/prepareRename`
    capabilities = types.ClientCapabilities(
        text_document=types.TextDocumentClientCapabilities(
            rename=types.RenameClientCapabilities(prepare_support=True)
        )
    )
    async for result in get_client_for("rename.py", capabilities):
        yield result


@pytest.mark.parametrize(
    "position, expected",
    [
        (types.Position(line=5, character=1), None),
        (
            types.Position(line=5, character=6),
            types.PrepareRenameDefaultBehavior(default_behavior=True),
        ),
    ],
)
async def test_prepare_rename(
    rename: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
    position: types.Position,
    expected,
):
    """Ensure that the prepare rename handler in the server works as expected."""
    client, initialize_result = rename

    rename_options = initialize_result.capabilities.rename_provider
    assert rename_options == types.RenameOptions(prepare_provider=True)

    test_uri = uri_for("code.txt")
    test_path = path_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                text=test_path.read_text(),
            )
        )
    )

    result = await client.text_document_prepare_rename_async(
        types.PrepareRenameParams(
            position=position, text_document=types.TextDocumentIdentifier(uri=test_uri)
        )
    )

    if expected is None:
        assert result is None

    else:
        assert result == expected


@pytest.mark.parametrize(
    "position, expected",
    [
        (types.Position(line=5, character=1), None),
        (
            types.Position(line=3, character=6),
            (
                types.TextEdit(
                    new_text="my_name",
                    range=types.Range(
                        start=types.Position(line=3, character=3),
                        end=types.Position(line=3, character=7),
                    ),
                ),
                types.TextEdit(
                    new_text="my_name",
                    range=types.Range(
                        start=types.Position(line=5, character=45),
                        end=types.Position(line=5, character=49),
                    ),
                ),
            ),
        ),
    ],
)
async def test_rename(
    rename: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
    position: types.Position,
    expected,
):
    """Ensure that the rename handler in the server works as expected."""
    client, initialize_result = rename

    rename_options = initialize_result.capabilities.rename_provider
    assert rename_options == types.RenameOptions(prepare_provider=True)

    test_uri = uri_for("code.txt")
    test_path = path_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                text=test_path.read_text(),
            )
        )
    )

    result = await client.text_document_rename_async(
        types.RenameParams(
            new_name="my_name",
            position=position,
            text_document=types.TextDocumentIdentifier(uri=test_uri),
        )
    )

    if expected is None:
        assert result is None

    else:
        # https://catt.rs/en/latest/migrations.html#sequences-structuring-into-tuples
        seq = type(cattrs.structure([], Sequence[str]))
        assert result == types.WorkspaceEdit(changes={test_uri: seq(expected)})
