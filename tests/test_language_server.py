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
import pathlib
from time import sleep

import pytest

from pygls import IS_PYODIDE
from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_DID_OPEN,
    WORKSPACE_EXECUTE_COMMAND,
)
from lsprotocol.types import (
    ClientCapabilities,
    DidOpenTextDocumentParams,
    ExecuteCommandParams,
    InitializeParams,
    TextDocumentItem,
)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from . import CMD_ASYNC, CMD_SYNC, CMD_THREAD


def _initialize_server(server):
    server.lsp.lsp_initialize(
        InitializeParams(
            process_id=1234,
            root_uri=pathlib.Path(__file__).parent.as_uri(),
            capabilities=ClientCapabilities(),
        )
    )


def test_bf_initialize(client_server):
    client, server = client_server
    root_uri = pathlib.Path(__file__).parent.as_uri()
    process_id = 1234

    response = client.lsp.send_request(
        INITIALIZE,
        InitializeParams(
            process_id=process_id,
            root_uri=root_uri,
            capabilities=ClientCapabilities(),
        ),
    ).result()

    assert server.process_id == process_id
    assert server.workspace.root_uri == root_uri
    assert response.capabilities is not None


def test_bf_text_document_did_open(client_server):
    client, server = client_server

    _initialize_server(server)

    client.lsp.notify(
        TEXT_DOCUMENT_DID_OPEN,
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=__file__, language_id="python", version=1, text="test"
            )
        ),
    )

    sleep(1)

    assert len(server.lsp.workspace.documents) == 1

    document = server.workspace.get_document(__file__)
    assert document.uri == __file__
    assert document.version == 1
    assert document.source == "test"
    assert document.language_id == "python"


@pytest.mark.skipif(IS_PYODIDE, reason='threads are not available in pyodide.')
def test_command_async(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_ASYNC)
    ).result()

    assert is_called
    assert thread_id == server.thread_id


@pytest.mark.skipif(IS_PYODIDE, reason='threads are not available in pyodide.')
def test_command_sync(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_SYNC)
    ).result()

    assert is_called
    assert thread_id == server.thread_id


@pytest.mark.skipif(IS_PYODIDE, reason='threads are not available in pyodide.')
def test_command_thread(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_THREAD)
    ).result()

    assert is_called
    assert thread_id != server.thread_id


def test_allow_custom_protocol_derived_from_lsp():
    class CustomProtocol(LanguageServerProtocol):
        pass

    server = LanguageServer('pygls-test', 'v1', protocol_cls=CustomProtocol)

    assert isinstance(server.lsp, CustomProtocol)


def test_forbid_custom_protocol_not_derived_from_lsp():
    class CustomProtocol:
        pass

    with pytest.raises(TypeError):
        LanguageServer('pygls-test', 'v1', protocol_cls=CustomProtocol)
