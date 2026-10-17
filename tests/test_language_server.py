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
import json
import pathlib
from threading import Event
from time import sleep
from unittest.mock import Mock

import pytest

from pygls import IS_PYODIDE
from lsprotocol.types import (
    INITIALIZE,
    SHUTDOWN,
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
from pygls.lsp.server import LanguageServer
from . import CMD_ASYNC, CMD_SYNC, CMD_THREAD


def _initialize_server(server):
    server.protocol.lsp_initialize(
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

    response = client.protocol.send_request(
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

    client.protocol.notify(
        TEXT_DOCUMENT_DID_OPEN,
        DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=__file__, language_id="python", version=1, text="test"
            )
        ),
    )

    sleep(1)

    assert len(server.protocol.workspace.text_documents) == 1

    document = server.workspace.get_text_document(__file__)
    assert document.uri == __file__
    assert document.version == 1
    assert document.source == "test"
    assert document.language_id == "python"


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
def test_command_async(client_server):
    client, server = client_server

    is_called, thread_id = client.protocol.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_ASYNC)
    ).result()

    assert is_called
    assert thread_id == server.thread_id


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
def test_command_sync(client_server):
    client, server = client_server

    is_called, thread_id = client.protocol.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_SYNC)
    ).result()

    assert is_called
    assert thread_id == server.thread_id


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
def test_command_thread(client_server):
    client, server = client_server

    is_called, thread_id = client.protocol.send_request(
        WORKSPACE_EXECUTE_COMMAND, ExecuteCommandParams(command=CMD_THREAD)
    ).result()

    assert is_called
    assert thread_id != server.thread_id


def test_allow_custom_protocol_derived_from_lsp():
    class CustomProtocol(LanguageServerProtocol):
        pass

    server = LanguageServer("pygls-test", "v1", protocol_cls=CustomProtocol)

    assert isinstance(server.protocol, CustomProtocol)


def test_forbid_custom_protocol_not_derived_from_lsp():
    class CustomProtocol:
        pass

    with pytest.raises(TypeError):
        LanguageServer("pygls-test", "v1", protocol_cls=CustomProtocol)


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
def test_shutdown_cancels_queued_threaded_requests():
    """Cancelling queued requests runs callbacks that remove their futures."""
    server = LanguageServer("pygls-test", "v1", max_workers=1)
    protocol = server.protocol
    writer = Mock()
    writer.write.return_value = None
    protocol.set_writer(writer, include_headers=False)
    started = Event()
    release = Event()

    @server.thread()
    @server.feature("test/blocking")
    def blocking(params):
        started.set()
        assert release.wait(timeout=10)

    try:
        protocol._handle_request(1, "test/blocking", None)
        assert started.wait(timeout=5)
        running = protocol._request_futures[1]

        # Keep the only worker busy so these requests can be cancelled reliably.
        protocol._handle_request(2, "test/blocking", None)
        protocol._handle_request(3, "test/blocking", None)
        queued = [protocol._request_futures[i] for i in (2, 3)]
        assert all(not future.running() for future in queued)

        protocol._handle_request(4, SHUTDOWN, None)

        messages = [json.loads(args.args[0]) for args in writer.write.call_args_list]
        responses = {message["id"]: message for message in messages}
        assert responses[4] == {"id": 4, "jsonrpc": "2.0", "result": None}
        assert all(future.cancelled() for future in queued)
        assert all(responses[i]["error"]["code"] == -32800 for i in (2, 3))
        assert protocol._shutdown
        assert running.running()
        assert set(protocol._request_futures) == {1}
    finally:
        release.set()
        server.shutdown()

    assert running.done()
    assert protocol._request_futures == {}
