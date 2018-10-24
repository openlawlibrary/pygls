# ##########################################################################
# # Copyright (c) Open Law Library. All rights reserved.                   #
# # See ThirdPartyNotices.txt in the project root for license information. #
# ##########################################################################
import os
import threading

import pytest
from pygls.features import WORKSPACE_EXECUTE_COMMAND
from pygls.types import ExecuteCommandParams, InitializeParams, \
    InitializeResult
from tests import CMD_ASYNC, CMD_SYNC, CMD_THREAD, FEATURE_ASYNC, \
    FEATURE_SYNC, FEATURE_THREAD
from tests.fixtures import client_server

CALL_TIMEOUT = 2


def test_initialize(client_server):
    client, _ = client_server
    response = client.lsp._send_request(
        'initialize',
        InitializeParams(
            process_id=1234,
            root_path=os.path.dirname(__file__)
        )
    ).result(timeout=CALL_TIMEOUT)
    assert hasattr(response, 'capabilities')


def test_feature_async(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(FEATURE_ASYNC, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_feature_sync(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(FEATURE_SYNC, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_feature_thread(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(FEATURE_THREAD, {}) \
                                     .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id != server.thread_id


def test_command_async(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(WORKSPACE_EXECUTE_COMMAND,
                                                    ExecuteCommandParams(
                                                        CMD_ASYNC
                                                    ))\
        .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_command_sync(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(WORKSPACE_EXECUTE_COMMAND,
                                                    ExecuteCommandParams(
                                                        CMD_SYNC
                                                    ))\
        .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id == server.thread_id


def test_command_thread(client_server):
    client, server = client_server

    is_called, thread_id = client.lsp._send_request(WORKSPACE_EXECUTE_COMMAND,
                                                    ExecuteCommandParams(
                                                        CMD_THREAD
                                                    ))\
        .result(timeout=CALL_TIMEOUT)

    assert is_called
    assert thread_id != server.thread_id
