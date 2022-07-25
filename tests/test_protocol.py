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
import io
import json
from concurrent.futures import Future
from functools import partial
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import pytest

from pygls.exceptions import JsonRpcException, JsonRpcInvalidParams
from pygls.lsp import Model, get_method_params_type
from pygls.lsp.types import (
    ClientCapabilities,
    CompletionItem,
    CompletionItemKind,
    InitializeParams,
    InitializeResult,
    ProgressParams,
    WorkDoneProgressBegin,
)
from pygls.protocol import (
    JsonRPCNotification,
    JsonRPCProtocol,
    JsonRPCRequestMessage,
    JsonRPCResponseMessage,
)
from pygls.protocol import deserialize_message as _deserialize_message

TEST_METHOD = "test_method"


class FeatureParams(Model):
    class InnerType(Model):
        inner_field: str

    field_a: str
    field_b: Optional[InnerType] = None


TEST_LSP_METHODS_MAP = {
    TEST_METHOD: (None, FeatureParams, None),
}

deserialize_message = partial(
    _deserialize_message,
    get_params_type=partial(
        get_method_params_type, lsp_methods_map=TEST_LSP_METHODS_MAP
    ),
)


def test_deserialize_notification_message_valid_params():
    params = """
    {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": {
            "field_a": "test_a",
            "field_b": {
                "inner_field": "test_inner"
            }
        }
    }
    """

    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCNotification)
    assert result.jsonrpc == "2.0"

    assert isinstance(result.params, FeatureParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, FeatureParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_deserialize_notification_message_bad_params_should_raise_error():
    params = """
    {
        "jsonrpc": "2.0",
        "method": "test_method",
        "params": {
            "field_a": "test_a",
            "field_b": {
                "wrong_field_name": "test_inner"
            }
        }
    }
    """

    with pytest.raises(JsonRpcInvalidParams):
        json.loads(params, object_hook=deserialize_message)


@pytest.mark.parametrize(
    "params, expected",
    [
        (
            ProgressParams(
                token="id1",
                value=WorkDoneProgressBegin(
                    title="Begin progress",
                    percentage=0,
                ),
            ),
            {
                "jsonrpc": "2.0",
                "method": "test/notification",
                "params": {
                    "token": "id1",
                    "value": {
                        "kind": "begin",
                        "percentage": 0,
                        "title": "Begin progress",
                    },
                },
            },
        ),
    ],
)
def test_serialize_notification_message(params, expected):
    """
    Ensure that we can serialize notification messages, retaining all
    expected fields.
    """

    buffer = io.StringIO()

    protocol = JsonRPCProtocol(None)
    protocol._send_only_body = True
    protocol.connection_made(buffer)

    protocol.notify("test/notification", params=params)
    actual = json.loads(buffer.getvalue())

    assert actual == expected


def test_deserialize_response_message():
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    """
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCResponseMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.result == "1"
    assert result.error is None


def test_deserialize_request_message_with_registered_type():
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "method": "test_method",
        "params": {
            "field_a": "test_a",
            "field_b": {
                "inner_field": "test_inner"
            }
        }
    }
    """
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCRequestMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"

    assert isinstance(result.params, FeatureParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, FeatureParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_deserialize_request_message_without_registered_type():
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "method": "random",
        "params": {
            "field_a": "test_a",
            "field_b": {
                "inner_field": "test_inner"
            }
        }
    }
    """
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCRequestMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"

    assert type(result.params).__name__ == "Object"
    assert result.params.field_a == "test_a"
    assert result.params.field_b.inner_field == "test_inner"


@pytest.mark.parametrize(
    "result, expected",
    [
        (None, {"jsonrpc": "2.0", "id": "1", "result": None}),
        (
            [
                CompletionItem(label="example-one"),
                CompletionItem(
                    label="example-two",
                    kind=CompletionItemKind.Class,
                    preselect=False,
                    deprecated=True,
                ),
            ],
            {
                "jsonrpc": "2.0",
                "id": "1",
                "result": [
                    {"label": "example-one"},
                    {
                        "label": "example-two",
                        "kind": 7,  # CompletionItemKind.Class
                        "preselect": False,
                        "deprecated": True,
                    },
                ],
            },
        ),
    ],
)
def test_serialize_response_message(result, expected):
    """
    Ensure that we can serialize response messages, retaining all expected
    fields.
    """

    buffer = io.StringIO()

    protocol = JsonRPCProtocol(None)
    protocol._send_only_body = True
    protocol.connection_made(buffer)

    protocol._send_response("1", result=result)
    actual = json.loads(buffer.getvalue())

    assert actual == expected


def test_data_received_without_content_type(client_server):
    _, server = client_server
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": 1,
        }
    )
    message = "\r\n".join(
        (
            "Content-Length: " + str(len(body)),
            "",
            body,
        )
    )
    data = bytes(message, "utf-8")
    server.lsp.data_received(data)


def test_data_received_content_type_first_should_handle_message(client_server):
    _, server = client_server
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": 1,
        }
    )
    message = "\r\n".join(
        (
            "Content-Type: application/vscode-jsonrpc; charset=utf-8",
            "Content-Length: " + str(len(body)),
            "",
            body,
        )
    )
    data = bytes(message, "utf-8")
    server.lsp.data_received(data)


def dummy_message(param=1):
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "test",
            "params": param,
        }
    )
    message = "\r\n".join(
        (
            "Content-Length: " + str(len(body)),
            "Content-Type: application/vscode-jsonrpc; charset=utf-8",
            "",
            body,
        )
    )
    return bytes(message, "utf-8")


def test_data_received_single_message_should_handle_message(client_server):
    _, server = client_server
    data = dummy_message()
    server.lsp.data_received(data)


def test_data_received_partial_message_should_handle_message(client_server):
    _, server = client_server
    data = dummy_message()
    partial = len(data) - 5
    server.lsp.data_received(data[:partial])
    server.lsp.data_received(data[partial:])


def test_data_received_multi_message_should_handle_messages(client_server):
    _, server = client_server
    messages = (dummy_message(i) for i in range(3))
    data = b"".join(messages)
    server.lsp.data_received(data)


def test_data_received_error_should_raise_jsonrpc_error(client_server):
    _, server = client_server
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": "err",
            "error": {
                "code": -1,
                "message": "message for you sir",
            },
        }
    )
    message = "\r\n".join(
        [
            "Content-Length: " + str(len(body)),
            "Content-Type: application/vscode-jsonrpc; charset=utf-8",
            "",
            body,
        ]
    ).encode("utf-8")
    future = server.lsp._server_request_futures["err"] = Future()
    server.lsp.data_received(message)
    with pytest.raises(JsonRpcException, match="message for you sir"):
        future.result()


def test_initialize_should_return_server_capabilities(client_server):
    _, server = client_server
    params = InitializeParams(
        process_id=1234,
        root_uri=Path(__file__).parent.as_uri(),
        capabilities=ClientCapabilities(),
    )

    server_capabilities = server.lsp.lsp_initialize(params)

    assert isinstance(server_capabilities, InitializeResult)


def test_ignore_unknown_notification(client_server):
    _, server = client_server

    fn = server.lsp._execute_notification
    server.lsp._execute_notification = Mock()

    server.lsp._handle_notification("random/notification", None)
    assert not server.lsp._execute_notification.called

    # Remove mock
    server.lsp._execute_notification = fn
