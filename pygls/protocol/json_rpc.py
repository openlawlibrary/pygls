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
import enum
import json
import logging
import typing
from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Protocol
from typing import Type
from typing import Union
from uuid import uuid4

import attrs
import cattrs

from pygls.exceptions import JsonRpcInternalError
from pygls.exceptions import JsonRpcInvalidParams

MsgId = Union[str, int]
ConverterFactory = Callable[[], cattrs.Converter]
IdFactory = Callable[[], MsgId]


def uuids():
    return str(uuid4())


@typing.runtime_checkable
class JsonRPCNotification(Protocol):
    """Represents the generic shape of a json rpc notification message."""

    method: str
    jsonrpc: str
    params: Any


@typing.runtime_checkable
class JsonRPCRequestMessage(Protocol):
    """Represents the generic shape of a json rpc request message."""

    id: MsgId
    method: str
    jsonrpc: str
    params: Any


@typing.runtime_checkable
class JsonRPCResultMessage(Protocol):
    """Represents the generic shape of a json rpc result message."""

    id: MsgId
    jsonrpc: str
    result: Any


@attrs.define
class ResponseError:
    code: int

    message: str

    data: Optional[Any] = None


@attrs.define
class JsonRPCErrorMessage:
    """Type representing a json rpc error message."""

    id: MsgId
    jsonrpc: str
    error: ResponseError


JsonRPCMessage = Union[
    JsonRPCErrorMessage,
    JsonRPCNotification,
    JsonRPCRequestMessage,
    JsonRPCResultMessage,
]


def basic_converter():
    converter = cattrs.Converter()
    converter.register_structure_hook(Union[str, int], lambda o, t: o)

    return converter


class JsonRPCProtocol:
    """JSON-RPC implementation."""

    CONTENT_TYPE = "application/vscode-jsonrpc"

    VERSION = "2.0"

    def __init__(
        self,
        converter_factory: ConverterFactory = basic_converter,
        encoding: str = "utf-8",
        id_factory: IdFactory = uuids,
        logger: Optional[logging.Logger] = None,
    ):
        self.converter = converter_factory()
        self.id_factory = id_factory
        self.encoding = encoding
        self.logger = logger or logging.getLogger(__name__)

        self._result_types: Dict[
            Union[int, str], Optional[Type[JsonRPCResultMessage]]
        ] = {}

    def get_notification_type(self, method: str) -> Optional[Type[JsonRPCNotification]]:
        """Return the type definition of the notification associated with the given
        method."""
        return None

    def get_request_type(self, method: str) -> Optional[Type[JsonRPCRequestMessage]]:
        """Return the type definition of the result associated with the given method."""
        return None

    def get_result_type(self, method: str) -> Optional[Type[JsonRPCResultMessage]]:
        """Return the type definition of the result associated with the given method."""
        return None

    def make_id(self) -> MsgId:
        """Return a new message id."""
        # TODO: Include logic to make sure this is unique?
        return self.id_factory()

    def encode_request(
        self,
        method: str,
        params: Optional[Any] = None,
        msg_id: Optional[MsgId] = None,
        include_headers: bool = True,
    ) -> bytes:
        """Construct a JSON-RPC request to send."""

        msg_id = msg_id or self.make_id()

        request_type = self.get_request_type(method) or _Request
        request = request_type(
            id=msg_id, method=method, params=params, jsonrpc=self.VERSION
        )

        # Lookup what the expected result type is for this message
        self._result_types[msg_id] = self.get_result_type(method)

        return self._encode_message(request, include_headers=include_headers)

    def encode_notification(
        self, method: str, params: Optional[Any] = None, include_headers: bool = True
    ) -> bytes:
        """Construct a JSON-RPC notification to send."""

        notification_type = self.get_notification_type(method) or _Notification
        notification = notification_type(
            method=method, params=params, jsonrpc=self.VERSION
        )

        return self._encode_message(notification, include_headers=include_headers)

    def encode_error(
        self, msg_id: MsgId, error: ResponseError, include_headers: bool = True
    ) -> bytes:
        """Construct a JSON-RPC error to send."""

        response = JsonRPCErrorMessage(id=msg_id, error=error, jsonrpc=self.VERSION)
        return self._encode_message(response, include_headers=include_headers)

    def encode_result(
        self, msg_id: MsgId, result: Optional[Any] = None, include_headers: bool = True
    ) -> bytes:
        """Construct a JSON-RPC result to send."""

        response_type = self._result_types.pop(msg_id, None) or _Result
        response = response_type(id=msg_id, result=result, jsonrpc=self.VERSION)

        return self._encode_message(response, include_headers=include_headers)

    def _encode_message(self, data: Any, include_headers: bool) -> bytes:
        """Encode the given data as bytes"""
        body = json.dumps(data, default=self._serialize_message)
        self.logger.debug("%s", body)

        if include_headers:
            header = (
                f"Content-Length: {len(body)}\r\n"
                f"Content-Type: {self.CONTENT_TYPE}; charset={self.encoding}\r\n\r\n"
            ).encode(self.encoding)
            return header + body.encode(self.encoding)

        return body.encode(self.encoding)

    def decode_message(self, data: bytes) -> JsonRPCMessage:
        body = data.decode(self.encoding)
        self.logger.debug(body)
        return json.loads(body, object_hook=self._deserialize_message)

    def _serialize_message(self, data: Any) -> Any:
        """Serialize data to JSON."""
        if hasattr(data, "__attrs_attrs__"):
            return self.converter.unstructure(data)

        if isinstance(data, enum.Enum):
            return data.value

        return data.__dict__

    def _deserialize_message(self, data: Any) -> Any:
        """Deserialize data from JSON."""

        if "jsonrpc" not in data:
            return data

        try:
            if "id" in data:
                if "error" in data:
                    return self.converter.structure(data, JsonRPCErrorMessage)
                elif "method" in data:
                    request_type = self.get_request_type(data["method"]) or _Request
                    return self.converter.structure(data, request_type)
                else:
                    response_type = self._result_types.pop(data["id"]) or _Result
                    return self.converter.structure(data, response_type)

            else:
                method = data.get("method", "")
                notification_type = self.get_notification_type(method) or _Notification
                return self.converter.structure(data, notification_type)

        except cattrs.ClassValidationError as exc:
            self.logger.error("Unable to deserialize message\n%s", exc_info=True)
            raise JsonRpcInvalidParams() from exc

        except Exception as exc:
            self.logger.error("Unable to deserialize message\n%s", exc_info=True)
            raise JsonRpcInternalError() from exc


@attrs.define
class _Notification:
    """Fallback type representing a generic json rpc notification message."""

    method: str
    jsonrpc: str
    params: Any


@attrs.define
class _Request:
    """Fallback type representing a generic json rpc request message."""

    id: MsgId
    method: str
    jsonrpc: str
    params: Any


@attrs.define
class _Result:
    """Fallback type representing a generic json rpc result message."""

    id: MsgId
    jsonrpc: str
    result: Any
