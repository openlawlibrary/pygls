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
from __future__ import annotations

import asyncio
import enum
import inspect
import json
import logging
import sys
import traceback
import typing
import uuid
from concurrent.futures import Future
from functools import partial
from typing import Any, Callable, Type, Union

import attrs
from cattrs.errors import ClassValidationError
from lsprotocol.types import (
    CANCEL_REQUEST,
    EXIT,
    WORKSPACE_EXECUTE_COMMAND,
    ResponseError,
    ResponseErrorMessage,
)

from pygls.exceptions import (
    FeatureNotificationError,
    FeatureRequestError,
    JsonRpcException,
    JsonRpcInternalError,
    JsonRpcInvalidParams,
    JsonRpcMethodNotFound,
    JsonRpcRequestCancelled,
)
from pygls.feature_manager import FeatureManager, is_thread_function

if typing.TYPE_CHECKING:
    from cattrs import Converter

    from pygls.io_ import AsyncWriter, Writer
    from pygls.server import JsonRPCServer

    MessageHandler = Union[Callable[[Any], Any],]
    MessageCallback = Callable[[Future[Any]], None]

logger = logging.getLogger(__name__)


@attrs.define
class JsonRPCNotification:
    """A class that represents a generic json rpc notification message.
    Used as a fallback for unknown types.
    """

    method: str
    jsonrpc: str
    params: Any


@attrs.define
class JsonRPCRequestMessage:
    """A class that represents a generic json rpc request message.
    Used as a fallback for unknown types.
    """

    id: Union[int, str]
    method: str
    jsonrpc: str
    params: Any


@attrs.define
class JsonRPCResponseMessage:
    """A class that represents a generic json rpc response message.
    Used as a fallback for unknown types.
    """

    id: Union[int, str]
    jsonrpc: str
    result: Any


class JsonRPCProtocol:
    """Json RPC protocol implementation

    Specification of the protocol can be found here:
        https://www.jsonrpc.org/specification

    This class provides bidirectional communication which is needed for LSP.
    """

    CHARSET = "utf-8"
    CONTENT_TYPE = "application/vscode-jsonrpc"
    VERSION = "2.0"

    def __init__(self, server: JsonRPCServer, converter: Converter):
        self._server = server
        self._converter = converter

        self._shutdown = False

        # Book keeping for in-flight requests
        self._request_futures: dict[str | int, Future[Any]] = {}
        self._result_types: dict[str | int, Any] = {}

        self.fm = FeatureManager(server, converter)
        self.writer: AsyncWriter | Writer | None = None
        self._include_headers = False

    def __call__(self):
        return self

    def _execute_handler(
        self,
        msg_id: str | int,
        handler: MessageHandler,
        params: Any,
        callback: MessageCallback,
    ):
        """Execute the given message handler.

        Parameters
        ----------
        msg_id
           The id of the message being handled

        handler
           The request handler to call

        params
           The parameters object to pass to the handler

        callback
           An optional callback function to call upon completion of the handler
        """

        if asyncio.iscoroutinefunction(handler):
            future = asyncio.ensure_future(handler(params))
            self._request_futures[msg_id] = future
            future.add_done_callback(callback)

        elif is_thread_function(handler):
            future = self._server.thread_pool.submit(handler, params)
            self._request_futures[msg_id] = future
            future.add_done_callback(callback)
        else:
            # While a future is not necessary for a synchronous function, it allows us to use a single
            # pattern across all handler types
            future: Future[Any] = Future()
            future.add_done_callback(callback)

            try:
                result = handler(params)
                future.set_result(result)
            except Exception as exc:
                future.set_exception(exc)

    def _send_handler_result(self, future: Future[Any], *, msg_id: str | int):
        """Callback function that sends the result of the given future to the client.

        Used to respond to request messages.
        """
        self._request_futures.pop(msg_id, None)

        try:
            if not future.cancelled():
                self._send_response(msg_id, result=future.result())
            else:
                self._send_response(
                    msg_id,
                    error=JsonRpcRequestCancelled(
                        f'Request with id "{msg_id}" is canceled'
                    ).to_response_error(),
                )
        except Exception:
            error = JsonRpcInternalError.of(sys.exc_info())
            logger.exception('Exception occurred for message "%s": %s', msg_id, error)
            self._send_response(msg_id, error=error.to_response_error())

    def _check_handler_result(self, future: Future[Any]):
        """Check the result of the future to see if an error occurred.

        Used when handling notification messages
        """
        if future.exception():
            try:
                raise future.exception()
            except Exception:
                error = JsonRpcInternalError.of(sys.exc_info())
                self._server._report_server_error(error, FeatureNotificationError)

    def _get_handler(self, feature_name):
        """Returns builtin or used defined feature by name if exists."""

        if (handler := self.fm.builtin_features.get(feature_name)) is not None:
            return handler

        if (handler := self.fm.features.get(feature_name)) is not None:
            return handler

        raise JsonRpcMethodNotFound.of(feature_name)

    def _handle_cancel_notification(self, msg_id):
        """Handles a cancel notification from the client."""
        future = self._request_futures.pop(msg_id, None)

        if not future:
            logger.warning('Cancel notification for unknown message id "%s"', msg_id)
            return

        # Will only work if the request hasn't started executing
        if future.cancel():
            logger.info('Cancelled request with id "%s"', msg_id)

    def _handle_notification(self, method_name, params):
        """Handles a notification from the client."""
        if method_name == CANCEL_REQUEST:
            self._handle_cancel_notification(params.id)
            return

        try:
            handler = self._get_handler(method_name)
            self._execute_handler(
                str(uuid.uuid4()), handler, params, self._check_handler_result
            )
        except JsonRpcMethodNotFound:
            logger.warning("Ignoring notification for unknown method %r", method_name)
        except Exception as error:
            logger.exception(
                "Failed to handle notification %r: %s",
                method_name,
                params,
                exc_info=True,
            )
            self._server._report_server_error(error, FeatureNotificationError)

    def _handle_request(self, msg_id, method_name, params):
        """Handles a request from the client."""
        try:
            handler = self._get_handler(method_name)

            # workspace/executeCommand is a special case
            if method_name == WORKSPACE_EXECUTE_COMMAND:
                handler(params, msg_id)
            else:
                self._execute_handler(
                    msg_id,
                    handler,
                    params,
                    callback=partial(self._send_handler_result, msg_id=msg_id),
                )

        except JsonRpcMethodNotFound as error:
            logger.warning(
                "Failed to handle request %r, unknown method %r",
                msg_id,
                method_name,
            )
            self._send_response(msg_id, None, error.to_response_error())
            self._server._report_server_error(error, FeatureRequestError)
        except JsonRpcException as error:
            logger.exception(
                "Failed to handle request %s %s %s",
                msg_id,
                method_name,
                params,
                exc_info=True,
            )
            self._send_response(msg_id, None, error.to_response_error())
            self._server._report_server_error(error, FeatureRequestError)
        except Exception as error:
            logger.exception(
                "Failed to handle request %s %s %s",
                msg_id,
                method_name,
                params,
                exc_info=True,
            )
            err = JsonRpcInternalError.of(sys.exc_info()).to_response_error()
            self._send_response(msg_id, None, err)
            self._server._report_server_error(error, FeatureRequestError)

    def _handle_response(self, msg_id, result=None, error=None):
        """Handles a response from the client."""
        future = self._request_futures.pop(msg_id, None)

        if not future:
            logger.warning('Received response to unknown message id "%s"', msg_id)
            return

        if error is not None:
            logger.debug('Received error response to message "%s": %s', msg_id, error)
            future.set_exception(JsonRpcException.from_error(error))
        else:
            logger.debug('Received result for message "%s": %s', msg_id, result)
            future.set_result(result)

    def _serialize_message(self, data):
        """Function used to serialize data sent to the client."""

        if hasattr(data, "__attrs_attrs__"):
            return self._converter.unstructure(data)

        if isinstance(data, enum.Enum):
            return data.value

        return data.__dict__

    def structure_message(self, data):
        """Function used to deserialize data recevied from the client."""

        if "jsonrpc" not in data:
            return data

        try:
            if "id" in data:
                if "error" in data:
                    return self._converter.structure(data, ResponseErrorMessage)
                elif "method" in data:
                    request_type = (
                        self.get_message_type(data["method"]) or JsonRPCRequestMessage
                    )
                    return self._converter.structure(data, request_type)
                else:
                    response_type = (
                        self._result_types.pop(data["id"]) or JsonRPCResponseMessage
                    )
                    return self._converter.structure(data, response_type)

            else:
                method = data.get("method", "")
                notification_type = self.get_message_type(method) or JsonRPCNotification
                return self._converter.structure(data, notification_type)

        except ClassValidationError as exc:
            logger.error("Unable to deserialize message\n%s", traceback.format_exc())
            raise JsonRpcInvalidParams() from exc

        except Exception as exc:
            logger.error("Unable to deserialize message\n%s", traceback.format_exc())
            raise JsonRpcInternalError() from exc

    def handle_message(self, message):
        """Delegates message to handlers depending on message type."""

        if message.jsonrpc != JsonRPCProtocol.VERSION:
            logger.warning('Unknown message "%s"', message)
            return

        if self._shutdown and getattr(message, "method", "") != EXIT:
            logger.warning("Server shutting down. No more requests!")
            return

        if hasattr(message, "method"):
            if hasattr(message, "id"):
                logger.debug("Request message received.")
                self._handle_request(message.id, message.method, message.params)
            else:
                logger.debug("Notification message received.")
                self._handle_notification(message.method, message.params)
        else:
            if hasattr(message, "error"):
                logger.debug("Error message received.")
                self._handle_response(message.id, None, message.error)
            else:
                logger.debug("Response message received.")
                self._handle_response(message.id, message.result)

    def _send_data(self, data):
        """Sends data to the client."""
        if not data:
            return

        if self.writer is None:
            logger.error("Unable to send data, no available transport!")
            return

        try:
            body = json.dumps(data, default=self._serialize_message)
            logger.info("Sending data: %s", body)

            if self._include_headers:
                header = (
                    f"Content-Length: {len(body)}\r\n"
                    f"Content-Type: {self.CONTENT_TYPE}; charset={self.CHARSET}\r\n\r\n"
                )
                data = header + body
            else:
                data = body

            res = self.writer.write(data.encode(self.CHARSET))
            if inspect.isawaitable(res):
                asyncio.ensure_future(res)

        except Exception as error:
            logger.exception("Error sending data", exc_info=True)
            self._server._report_server_error(error, JsonRpcInternalError)

    def _send_response(
        self, msg_id, result=None, error: Union[ResponseError, None] = None
    ):
        """Sends a JSON RPC response to the client.

        Args:
            msg_id(str): Id from request
            result(any): Result returned by handler
            error(any): Error returned by handler
        """

        if error is not None:
            response = ResponseErrorMessage(id=msg_id, error=error)

        else:
            response_type = self._result_types.pop(msg_id, JsonRPCResponseMessage)
            response = response_type(
                id=msg_id, result=result, jsonrpc=JsonRPCProtocol.VERSION
            )

        self._send_data(response)

    def set_writer(
        self,
        writer: AsyncWriter | Writer,
        include_headers: bool = True,
    ):
        """Set the writer object to use when sending data

        Parameters
        ----------
        writer
           The writer object

        include_headers
           Flag indicating if headers like ``Content-Length`` should be included when
           sending data. (Default ``True``)
        """
        self.writer = writer
        self._include_headers = include_headers

    def get_message_type(self, method: str) -> Type[Any] | None:
        """Return the type definition of the message associated with the given method."""
        return None

    def get_result_type(self, method: str) -> Type[Any] | None:
        """Return the type definition of the result associated with the given method."""
        return None

    def notify(self, method: str, params=None):
        """Sends a JSON RPC notification to the client."""

        logger.debug("Sending notification: '%s' %s", method, params)

        notification_type = self.get_message_type(method) or JsonRPCNotification
        notification = notification_type(
            method=method, params=params, jsonrpc=JsonRPCProtocol.VERSION
        )

        self._send_data(notification)

    def send_request(self, method, params=None, callback=None, msg_id=None):
        """Sends a JSON RPC request to the client.

        Args:
            method(str): The method name of the message to send
            params(any): The payload of the message

        Returns:
            Future that will be resolved once a response has been received
        """

        if msg_id is None:
            msg_id = str(uuid.uuid4())

        request_type = self.get_message_type(method) or JsonRPCRequestMessage
        logger.debug('Sending request with id "%s": %s %s', msg_id, method, params)

        request = request_type(
            id=msg_id,
            method=method,
            params=params,
            jsonrpc=JsonRPCProtocol.VERSION,
        )

        future = Future()  # type: ignore[var-annotated]
        # If callback function is given, call it when result is received
        if callback:

            def wrapper(future: Future):
                result = future.result()
                logger.info("Client response for %s received: %s", params, result)
                callback(result)

            future.add_done_callback(wrapper)

        self._request_futures[msg_id] = future
        self._result_types[msg_id] = self.get_result_type(method)

        self._send_data(request)

        return future

    def send_request_async(self, method, params=None, msg_id=None):
        """Calls `send_request` and wraps `concurrent.futures.Future` with
        `asyncio.Future` so it can be used with `await` keyword.

        Args:
            method(str): The method name of the message to send
            params(any): The payload of the message
            msg_id(str|int): Optional, message id

        Returns:
            `asyncio.Future` that can be awaited
        """
        return asyncio.wrap_future(
            self.send_request(method, params=params, msg_id=msg_id)
        )
