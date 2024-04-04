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

import typing

import pytest
import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import LanguageClient


@pytest_asyncio.fixture(scope="module")
async def code_lens(get_client_for):
    async for result in get_client_for("code_lens.py"):
        yield result


@pytest.mark.asyncio(scope="module")
async def test_code_lens(
    code_lens: Tuple[LanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example code lens server is working as expected."""
    client, initialize_result = code_lens

    code_lens_options = initialize_result.capabilities.code_lens_provider
    assert code_lens_options.resolve_provider is True

    test_uri = uri_for("sums.txt")
    response = await client.text_document_code_lens(
        types.CodeLensParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
        )
    )
    assert response == [
        types.CodeLens(
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=0, character=7),
            ),
            data=dict(left=1, right=1, uri=test_uri),
        ),
        types.CodeLens(
            range=types.Range(
                start=types.Position(line=3, character=0),
                end=types.Position(line=3, character=7),
            ),
            data=dict(left=2, right=3, uri=test_uri),
        ),
        types.CodeLens(
            range=types.Range(
                start=types.Position(line=6, character=0),
                end=types.Position(line=6, character=7),
            ),
            data=dict(left=6, right=6, uri=test_uri),
        ),
    ]


@pytest.mark.asyncio(scope="module")
async def test_code_lens_resolve(
    code_lens: Tuple[LanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example code lens server can resolve a code lens correctly."""

    client, _ = code_lens

    test_uri = uri_for("sums.txt")
    lens = types.CodeLens(
        range=types.Range(
            start=types.Position(line=0, character=0),
            end=types.Position(line=1, character=0),
        ),
        data=dict(left=1, right=1, uri=test_uri),
    )

    result = await client.code_lens_resolve(lens)

    # The existing fields should not be modified.
    assert result.range == lens.range
    assert result.data == lens.data

    # The command field should also be filled in.
    assert result.command == types.Command(
        title="Evaluate 1 + 1",
        command="codeLens.evaluateSum",
        arguments=[dict(uri=test_uri, left=1, right=1, line=0)],
    )


@pytest.mark.asyncio(scope="module")
async def test_evaluate_sum(
    code_lens: Tuple[LanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example code lens server can execute the ``evaluateSum`` command
    correctly."""

    workspace_edit = []
    client, initialize_result = code_lens

    @client.feature(types.WORKSPACE_APPLY_EDIT)
    def on_edit(params: types.ApplyWorkspaceEditParams):
        workspace_edit.extend(params.edit.document_changes)
        return types.ApplyWorkspaceEditResult(applied=True)

    provider = initialize_result.capabilities.execute_command_provider
    assert provider.commands == ["codeLens.evaluateSum"]

    test_uri = uri_for("sums.txt")
    await client.workspace_execute_command(
        types.ExecuteCommandParams(
            command="codeLens.evaluateSum",
            arguments=[dict(uri=test_uri, left=1, right=1, line=0)],
        )
    )

    assert workspace_edit == [
        types.TextDocumentEdit(
            text_document=types.OptionalVersionedTextDocumentIdentifier(
                uri=test_uri,
                version=None,
            ),
            edits=[
                types.TextEdit(
                    new_text=f"1 + 1 = 2\n",
                    range=types.Range(
                        start=types.Position(line=0, character=0),
                        end=types.Position(line=1, character=0),
                    ),
                )
            ],
        )
    ]
