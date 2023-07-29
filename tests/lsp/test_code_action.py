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
import sys

import pytest
import pytest_asyncio
from lsprotocol.types import (
    ClientCapabilities,
    CodeActionContext,
    CodeActionKind,
    CodeActionParams,
    InitializeParams,
    Position,
    Range,
    TextDocumentIdentifier,
)

import pygls.uris as uri
from pygls import IS_PYODIDE
from pygls.lsp.client import LanguageClient


@pytest_asyncio.fixture()
async def client(server_dir):
    """Setup and teardown the client."""

    server_py = server_dir / "code_actions.py"

    client = LanguageClient("pygls-test-client", "0.1")
    await client.start_io(sys.executable, str(server_py))

    yield client

    await client.shutdown_async(None)
    client.exit(None)

    await client.stop()


@pytest.mark.skipif(IS_PYODIDE, reason="subprocesses are not available in pyodide.")
async def test_code_actions(client: LanguageClient, workspace_dir):
    """Ensure that the example code action server is working as expected."""

    response = await client.initialize_async(
        InitializeParams(
            capabilities=ClientCapabilities(),
            root_uri=uri.from_fs_path(str(workspace_dir)),
        )
    )
    assert response is not None

    code_action_options = response.capabilities.code_action_provider
    assert code_action_options.code_action_kinds == [CodeActionKind.QuickFix]

    test_uri = uri.from_fs_path(str(workspace_dir / "sums.txt"))
    assert test_uri is not None

    response = await client.text_document_code_action_async(
        CodeActionParams(
            text_document=TextDocumentIdentifier(uri=test_uri),
            range=Range(
                start=Position(line=0, character=0),
                end=Position(line=1, character=0),
            ),
            context=CodeActionContext(diagnostics=[]),
        )
    )

    assert len(response) == 1
    code_action = response[0]

    assert code_action.title == "Evaluate '1 + 1 ='"
    assert code_action.kind == CodeActionKind.QuickFix

    fix = code_action.edit.changes[test_uri][0]
    expected_range = Range(
        start=Position(line=0, character=0),
        end=Position(line=0, character=7),
    )

    assert fix.range == expected_range
    assert fix.new_text == "1 + 1 = 2!"
