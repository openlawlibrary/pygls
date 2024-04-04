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
import asyncio
import json
from typing import Optional

import attrs
import pytest

from pygls.exceptions import JsonRpcException
from pygls.exceptions import JsonRpcInvalidParams
from pygls.protocol import JsonRPCHandler
from pygls.protocol import JsonRPCProtocol
from pygls.protocol import basic_converter
from pygls.protocol.json_rpc import _Notification
from pygls.protocol.json_rpc import _Request
from pygls.protocol.json_rpc import _Result

EXAMPLE_NOTIFICATION = "example/notification"
EXAMPLE_REQUEST = "example/request"


@pytest.fixture()
def handler():
    return JsonRPCHandler(protocol=JsonRPCProtocol(basic_converter))


@attrs.define
class IntResult:
    id: str
    result: int
    jsonrpc: str = attrs.field(default="2.0")


@attrs.define
class ExampleParams:
    @attrs.define
    class InnerType:
        inner_field: str

    field_a: str
    field_b: Optional[InnerType] = None


@attrs.define
class ExampleNotification:
    jsonrpc: str = attrs.field(default="2.0")
    method: str = EXAMPLE_NOTIFICATION
    params: ExampleParams = attrs.field(default=None)


@attrs.define
class ExampleRequest:
    id: str
    jsonrpc: str = attrs.field(default="2.0")
    method: str = EXAMPLE_REQUEST
    params: ExampleParams = attrs.field(default=None)


METHOD_MAP = {
    EXAMPLE_NOTIFICATION: (ExampleNotification, None, ExampleParams, None),
    EXAMPLE_REQUEST: (ExampleRequest, None, ExampleParams, None),
}


class ExampleProtocol(JsonRPCProtocol):
    """A test example of creating a custom JsonRPCProtocol."""

    def get_notification_type(self, method: str):
        return METHOD_MAP.get(method, (None,))[0]

    def get_request_type(self, method: str):
        return METHOD_MAP.get(method, (None,))[0]


@pytest.fixture()
def protocol():
    return ExampleProtocol(basic_converter)


def test_decode_notification(protocol):
    """Ensure that we can decode a notification message correctly."""
    message = f"""
    {{
        "jsonrpc": "2.0",
        "method": "{EXAMPLE_NOTIFICATION}",
        "params": {{
            "field_a": "test_a",
            "field_b": {{
                "inner_field": "test_inner"
            }}
        }}
    }}
    """.encode()

    result = protocol.decode_message(message)

    assert isinstance(
        result, ExampleNotification
    ), f"Expected FeatureRequest instance, got {result}"
    assert result.jsonrpc == "2.0"
    assert result.method == EXAMPLE_NOTIFICATION

    assert isinstance(result.params, ExampleParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, ExampleParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_decode_notification_unknown_type(protocol):
    """Ensure that we can decode a notificiation, even when the message is not known to
    be part of the protocol."""
    message = b"""
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

    result = protocol.decode_message(message)

    assert isinstance(result, _Notification)
    assert result.jsonrpc == "2.0"
    assert result.method == "random"

    assert result.params["field_a"] == "test_a"
    assert result.params["field_b"]["inner_field"] == "test_inner"


def test_decode_notification_invalid_params(protocol):
    """Ensure that the appropriate error is raised when decoding a message with invalid
    parameters."""
    message = f"""
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
    """.encode()

    with pytest.raises(JsonRpcInvalidParams):
        protocol.decode_message(message)


def test_decode_message_custom_converter():
    """Ensure that we can decode messages with a user defined converter.

    Just for fun, let's create a converter that reverses all the keys in a dict.
    """
    message = b"""
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    """

    @attrs.define
    class egasseM:
        cprnosj: str
        di: str
        tluser: str

    def structure_hook(obj, cls):
        params = {k[::-1]: v for k, v in obj.items()}
        return cls(**params)

    def custom_converter():
        converter = basic_converter()
        converter.register_structure_hook(egasseM, structure_hook)
        return converter

    protocol = JsonRPCProtocol(custom_converter)
    protocol._result_types["id"] = egasseM
    result = protocol.decode_message(message)

    assert isinstance(result, egasseM)
    assert result.cprnosj == "2.0"
    assert result.di == "id"
    assert result.tluser == "1"


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (
            # Custom notification type.
            EXAMPLE_NOTIFICATION,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(inner_field="field two"),
            ),
            ExampleNotification(
                params=ExampleParams(
                    field_a="field one",
                    field_b=ExampleParams.InnerType(inner_field="field two"),
                )
            ),
        ),
        (
            # Custom notification with dict params.
            "random",
            {"fieldA": "field one", "fieldB": {"innerField": "field two"}},
            _Notification(
                jsonrpc="2.0",
                method="random",
                params={
                    "fieldA": "field one",
                    "fieldB": {
                        "innerField": "field two",
                    },
                },
            ),
        ),
    ],
)
def test_encode_notification_message(method, params, expected):
    """Ensure that we can encode notification messages."""

    protocol = ExampleProtocol(basic_converter)
    data = protocol.encode_notification(method, params=params, include_headers=False)
    actual = protocol.decode_message(data)

    assert actual == expected


def test_decode_response(protocol):
    """Ensure that we can decode response messages correctly."""
    message = b"""
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    """
    protocol._result_types["id"] = IntResult
    result = protocol.decode_message(message)

    assert isinstance(result, IntResult)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.result == 1


def test_decode_response_unknown_type(protocol):
    """Ensure that we can decode response messages, even when it is not known to the
    protocol."""
    message = b"""
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
    protocol._result_types["id"] = _Result
    result = protocol.decode_message(message)

    assert isinstance(result, _Result)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"

    assert result.result["field_a"] == "test_a"
    assert result.result["field_b"]["inner_field"] == "test_inner"


def test_decode_request(protocol):
    """Ensure that we can decode request messages."""
    message = f"""
    {{
        "jsonrpc": "2.0",
        "id": "id",
        "method": "{EXAMPLE_REQUEST}",
        "params": {{
            "field_a": "test_a",
            "field_b": {{
                "inner_field": "test_inner"
            }}
        }}
    }}
    """.encode()
    result = protocol.decode_message(message)

    assert isinstance(result, ExampleRequest)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.method == EXAMPLE_REQUEST

    assert isinstance(result.params, ExampleParams)
    assert result.params.field_a == "test_a"

    assert isinstance(result.params.field_b, ExampleParams.InnerType)
    assert result.params.field_b.inner_field == "test_inner"


def test_decode_request_without_registered_type(protocol):
    """Ensure that we can decode request messages, even when the type is not known to
    the protocol."""
    message = b"""
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
    result = protocol.decode_message(message)

    assert isinstance(result, _Request)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.method == "random"

    assert result.params["field_a"] == "test_a"
    assert result.params["field_b"]["inner_field"] == "test_inner"


@pytest.mark.parametrize(
    "msg_type, result, expected",
    [
        (  # Unknown type with object params.
            _Result,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(inner_field="field two"),
            ),
            _Result(
                id="1",
                jsonrpc="2.0",
                result={
                    "field_a": "field one",
                    "field_b": {"inner_field": "field two"},
                },
            ),
        ),
        (  # Unknown type with dict params.
            _Result,
            {"fieldA": "field one", "fieldB": {"innerField": "field two"}},
            _Result(
                id="1",
                jsonrpc="2.0",
                result={
                    "fieldA": "field one",
                    "fieldB": {"innerField": "field two"},
                },
            ),
        ),
    ],
)
def test_encode_response(msg_type, result, expected):
    """Ensure that we can encode response messages"""

    protocol = JsonRPCProtocol(basic_converter)
    protocol._result_types["1"] = msg_type

    data = protocol.encode_result("1", result=result, include_headers=False)

    protocol._result_types["1"] = msg_type
    actual = protocol.decode_message(data)

    assert actual == expected


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (  # Unknown type with object params.
            EXAMPLE_REQUEST,
            ExampleParams(
                field_a="field one",
                field_b=ExampleParams.InnerType(inner_field="field two"),
            ),
            _Request(
                jsonrpc="2.0",
                id="1",
                method=EXAMPLE_REQUEST,
                params={
                    "field_a": "field one",
                    "field_b": {"inner_field": "field two"},
                },
            ),
        ),
        (  # Unknown type with dict params.
            EXAMPLE_REQUEST,
            {"fieldA": "field one", "fieldB": {"innerField": "field two"}},
            _Request(
                jsonrpc="2.0",
                id="1",
                method=EXAMPLE_REQUEST,
                params={
                    "fieldA": "field one",
                    "fieldB": {"innerField": "field two"},
                },
            ),
        ),
    ],
)
def test_encode_request(method, params, expected):
    """Ensure that we can encode request messages."""

    protocol = JsonRPCProtocol(basic_converter)

    data = protocol.encode_request(method, params, msg_id="1", include_headers=False)
    actual = protocol.decode_message(data)

    assert actual == expected


@pytest.mark.asyncio
async def test_error_should_raise(handler: JsonRPCHandler):
    """Ensure that when an error response is received, an appropriate error is raised."""
    message = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": "err",
            "error": {
                "code": -1,
                "message": "message for you sir",
            },
        }
    ).encode()

    future = handler._futures["err"] = asyncio.get_running_loop().create_future()
    handler(message)

    with pytest.raises(JsonRpcException, match="message for you sir"):
        future.result()
