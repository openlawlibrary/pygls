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
    InlayHint,
    InlayHintParams,
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

    server_py = server_dir / "inlay_hints.py"

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

    inlay_hint_provider = response.capabilities.inlay_hint_provider
    assert inlay_hint_provider.resolve_provider is True

    test_uri = uri.from_fs_path(str(workspace_dir / "sums.txt"))
    assert test_uri is not None

    response = await client.text_document_inlay_hint_async(
        InlayHintParams(
            text_document=TextDocumentIdentifier(uri=test_uri),
            range=Range(
                start=Position(line=3, character=0),
                end=Position(line=4, character=0),
            ),
        )
    )

    assert len(response) == 2
    two, three = response[0], response[1]

    assert two.label == ":10"
    assert two.tooltip is None

    assert three.label == ":11"
    assert three.tooltip is None

    resolved = await client.inlay_hint_resolve_async(three)
    assert resolved.tooltip == "Binary representation of the number: 3"
