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
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import attrs
import pytest

from pygls.exceptions import JsonRpcException, JsonRpcInvalidParams
from lsprotocol.types import (
    PROGRESS,
    TEXT_DOCUMENT_COMPLETION,
    ClientCapabilities,
    CompletionItem,
    CompletionItemKind,
    CompletionParams,
    InitializeParams,
    InitializeResult,
    ProgressParams,
    Position,
    ShutdownResponse,
    TextDocumentCompletionResponse,
    TextDocumentIdentifier,
    WorkDoneProgressBegin,
)
from pygls.protocol import (
    default_converter,
    JsonRPCProtocol,
    JsonRPCRequestMessage,
    JsonRPCResponseMessage,
    JsonRPCNotification
)

EXAMPLE_NOTIFICATION = "example/notification"
EXAMPLE_REQUEST = "example/request"


@attrs.define
class IntResult:
    id: str
    result: int
    jsonrpc: str = attrs.field(default='2.0')


@attrs.define
class ExampleParams:
    @attrs.define
    class InnerType:
        inner_field: str

    field_a: str
    field_b: Optional[InnerType] = None


@attrs.define
class ExampleNotification:
    jsonrpc: str = attrs.field(default='2.0')
    method: str = EXAMPLE_NOTIFICATION
    params: ExampleParams = attrs.field(default=None)


@attrs.define
class ExampleRequest:
    id: str
    jsonrpc: str = attrs.field(default='2.0')
    method: str = EXAMPLE_REQUEST
    params: ExampleParams = attrs.field(default=None)


EXAMPLE_LSP_METHODS_MAP = {
    EXAMPLE_NOTIFICATION: (ExampleNotification, None, ExampleParams, None),
    EXAMPLE_REQUEST: (ExampleRequest, None, ExampleParams, None),
}


class ExampleProtocol(JsonRPCProtocol):

    def get_message_type(self, method: str):
        return EXAMPLE_LSP_METHODS_MAP.get(method, (None,))[0]


@pytest.fixture()
def protocol():
    return ExampleProtocol(None, default_converter())


def test_deserialize_notification_message_valid_params(protocol):
    params = f"""
    {{
        "jsonrpc": "2.0",
        "method": "{EXAMPLE_NOTIFICATION}",
        "params": {{
            "fieldA": "test_a",
            "fieldB": {{
                "innerField": "test_inner"
            }}
        }}
    }}
    """

    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, ExampleNotification), f"Expected FeatureRequest instance, got {result}"
    assert result.jsonrpc == "2.0"
    assert result.method == EXAMPLE_NOTIFICATION

    assert isinstance(result.params, ExampleParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, ExampleParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_deserialize_notification_message_unknown_type(protocol):
    params = """
    {
        "jsonrpc": "2.0",
        "method": "random",
        "params": {
            "field_a": "test_a",
            "field_b": {
                "inner_field": "test_inner"
            }
        }
    }
    """

    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, JsonRPCNotification)
    assert result.jsonrpc == "2.0"
    assert result.method == "random"

    assert result.params.field_a == "test_a"
    assert result.params.field_b.inner_field == "test_inner"


def test_deserialize_notification_message_bad_params_should_raise_error(protocol):
    params = f"""
    {{
        "jsonrpc": "2.0",
        "method": "{EXAMPLE_NOTIFICATION}",
        "params": {{
            "field_a": "test_a",
            "field_b": {{
                "wrong_field_name": "test_inner"
            }}
        }}
    }}
    """

    with pytest.raises(JsonRpcInvalidParams):
        json.loads(params, object_hook=protocol._deserialize_message)


def test_deserialize_response_message_custom_converter():
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    """
    # Just for fun, let's create a converter that reverses all the keys in a dict.
    #
    @attrs.define
    class egasseM:
        cprnosj: str
        di: str
        tluser: str

    def structure_hook(obj, cls):
        params = {k[::-1]: v for k, v in obj.items()}
        return cls(**params)

    def custom_converter():
        converter = default_converter()
        converter.register_structure_hook(egasseM, structure_hook)
        return converter

    protocol = JsonRPCProtocol(None, custom_converter())
    protocol._result_types["id"] = egasseM
    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, egasseM)
    assert result.cprnosj == "2.0"
    assert result.di == "id"
    assert result.tluser == "1"


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (
            # Known notification type.
            PROGRESS,
            ProgressParams(
                token="id1",
                value=WorkDoneProgressBegin(
                    title="Begin progress",
                    percentage=0,
                ),
            ),
            {
                "jsonrpc": "2.0",
                "method": "$/progress",
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
        (
            # Custom notification type.
            EXAMPLE_NOTIFICATION,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(
                    inner_field="field two"
                ),
            ),
            {
                "jsonrpc": "2.0",
                "method": EXAMPLE_NOTIFICATION,
                "params": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two",
                    },
                },
            },
        ),
        (
            # Custom notification with dict params.
            EXAMPLE_NOTIFICATION,
            {
                "fieldA": "field one",
                "fieldB": {
                    "innerField": "field two"
                }
            },
            {
                "jsonrpc": "2.0",
                "method": EXAMPLE_NOTIFICATION,
                "params": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two",
                    },
                },
            },
        )
    ],
)
def test_serialize_notification_message(method, params, expected):
    """
    Ensure that we can serialize notification messages, retaining all
    expected fields.
    """

    buffer = io.StringIO()

    protocol = JsonRPCProtocol(None, default_converter())
    protocol._send_only_body = True
    protocol.connection_made(buffer)

    protocol.notify(method, params=params)
    actual = json.loads(buffer.getvalue())

    assert actual == expected


def test_deserialize_response_message(protocol):
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    """
    protocol._result_types["id"] = IntResult
    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, IntResult)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.result == 1


def test_deserialize_response_message_unknown_type(protocol):
    params = """
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": {
            "field_a": "test_a",
            "field_b": {
                "inner_field": "test_inner"
            }
        }
    }
    """
    protocol._result_types["id"] = JsonRPCResponseMessage
    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, JsonRPCResponseMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"

    assert result.result.field_a == "test_a"
    assert result.result.field_b.inner_field == "test_inner"


def test_deserialize_request_message_with_registered_type(protocol):
    params = f"""
    {{
        "jsonrpc": "2.0",
        "id": "id",
        "method": "{EXAMPLE_REQUEST}",
        "params": {{
            "fieldA": "test_a",
            "fieldB": {{
                "innerField": "test_inner"
            }}
        }}
    }}
    """
    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, ExampleRequest)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.method == EXAMPLE_REQUEST

    assert isinstance(result.params, ExampleParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, ExampleParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_deserialize_request_message_without_registered_type(protocol):
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
    result = json.loads(params, object_hook=protocol._deserialize_message)

    assert isinstance(result, JsonRPCRequestMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.method == "random"

    assert result.params.field_a == "test_a"
    assert result.params.field_b.inner_field == "test_inner"


@pytest.mark.parametrize(
    "msg_type, result, expected",
    [
        (ShutdownResponse, None, {"jsonrpc": "2.0", "id": "1", "result": None}),
        (
            TextDocumentCompletionResponse,
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
        (   # Unknown type with object params.
            JsonRPCResponseMessage,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(inner_field="field two")
            ),
            {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two"
                    }
                },
            }
        ),
        (   # Unknown type with dict params.
            JsonRPCResponseMessage,
            {
                "fieldA": "field one",
                "fieldB": {
                    "innerField": "field two"
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "1",
                "result": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two"
                    }
                },
            }
        )
    ],
)
def test_serialize_response_message(msg_type, result, expected):
    """
    Ensure that we can serialize response messages, retaining all expected
    fields.
    """

    buffer = io.StringIO()

    protocol = JsonRPCProtocol(None, default_converter())
    protocol._send_only_body = True
    protocol.connection_made(buffer)

    protocol._result_types["1"] = msg_type

    protocol._send_response("1", result=result)
    actual = json.loads(buffer.getvalue())

    assert actual == expected


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (
            TEXT_DOCUMENT_COMPLETION,
            CompletionParams(
                text_document=TextDocumentIdentifier(uri="file:///file.txt"),
                position=Position(line=1, character=0)
            ),
            {
                "jsonrpc": "2.0",
                "id": "1",
                "method": TEXT_DOCUMENT_COMPLETION,
                "params": {
                    "textDocument": { "uri": "file:///file.txt" },
                    "position": { "line": 1, "character": 0 }
                },
            },
        ),
        (   # Unknown type with object params.
            EXAMPLE_REQUEST,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(inner_field="field two")
            ),
            {
                "jsonrpc": "2.0",
                "id": "1",
                "method": EXAMPLE_REQUEST,
                "params": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two"
                    }
                },
            }
        ),
        (   # Unknown type with dict params.
            EXAMPLE_REQUEST,
            {
                "fieldA": "field one",
                "fieldB": {
                    "innerField": "field two"
                }
            },
            {
                "jsonrpc": "2.0",
                "id": "1",
                "method": EXAMPLE_REQUEST,
                "params": {
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two"
                    }
                },
            }
        )
    ],
)
def test_serialize_request_message(method, params, expected):
    """
    Ensure that we can serialize request messages, retaining all expected
    fields.
    """

    buffer = io.StringIO()

    protocol = JsonRPCProtocol(None, default_converter())
    protocol._send_only_body = True
    protocol.connection_made(buffer)

    protocol.send_request(method, params, callback=None, msg_id="1")
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
    future = server.lsp._request_futures["err"] = Future()
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
