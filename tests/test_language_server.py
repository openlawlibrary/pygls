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
from pygls.features import (INITIALIZE, TEXT_DOCUMENT_DID_OPEN,
                            WORKSPACE_EXECUTE_COMMAND)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from pygls.types import (DidOpenTextDocumentParams, ExecuteCommandParams,
                         InitializeParams, TextDocumentItem)

from tests import (CMD_ASYNC, CMD_SYNC, CMD_THREAD, FEATURE_ASYNC,
                   FEATURE_SYNC, FEATURE_THREAD)

CALL_TIMEOUT = 2


def _initialize_server(server):
    server.lsp.bf_initialize(InitializeParams(
        process_id=1234,
        root_uri=pathlib.Path(__file__).parent.as_uri(),
        capabilities=None
    ))


def test_bf_initialize(client_server):
    client, server = client_server
    root_uri = pathlib.Path(__file__).parent.as_uri()
    process_id = 1234

    response = client.lsp.send_request(
        INITIALIZE,
        {
            "processId": process_id,
            "rootUri": root_uri,
            "capabilities": None
        }
    ).result(timeout=CALL_TIMEOUT)

    assert server.process_id == process_id
    assert server.workspace.root_uri == root_uri
    assert hasattr(response, 'capabilities')


def test_bf_text_document_did_open(client_server):
    client, server = client_server

    _initialize_server(server)

    client.lsp.notify(TEXT_DOCUMENT_DID_OPEN,
                      DidOpenTextDocumentParams(
                          TextDocumentItem(__file__, 'python', 1, 'test')
                      ))

    sleep(1)

    assert len(server.lsp.workspace.documents) == 1


def test_feature_async(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(FEATURE_ASYNC, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_feature_sync(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(FEATURE_SYNC, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_feature_thread(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(FEATURE_THREAD, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id != server.thread_id


def test_command_async(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp.send_request(WORKSPACE_EXECUTE_COMMAND,
                                                   ExecuteCommandParams(
                                                       CMD_ASYNC
                                                   ))\
        .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_command_sync(client_server):
    client, server = client_server

    is_called, thread_id = \
        client.lsp.send_request(
            WORKSPACE_EXECUTE_COMMAND,
            ExecuteCommandParams(
                CMD_SYNC
            )
        ).result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_command_thread(client_server):
    client, server = client_server

    is_called, thread_id = \
        client.lsp.send_request(
            WORKSPACE_EXECUTE_COMMAND,
            ExecuteCommandParams(
                CMD_THREAD
            )
        ).result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id != server.thread_id


def test_allow_custom_protocol_derived_from_lsp():
    class CustomProtocol(LanguageServerProtocol):
        pass

    server = LanguageServer(protocol_cls=CustomProtocol)

    assert isinstance(server.lsp, CustomProtocol)


def test_forbid_custom_protocol_not_derived_from_lsp():
    class CustomProtocol:
        pass

    with pytest.raises(TypeError):
        LanguageServer(protocol_cls=CustomProtocol)
