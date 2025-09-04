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
import contextvars
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
from typing import Any, Callable, Protocol, Type, Union, runtime_checkable

import attrs
from cattrs.errors import ClassValidationError
from lsprotocol.types import (
    CANCEL_REQUEST,
    EXIT,
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
    from collections.abc import Generator

    from cattrs import Converter

    from pygls.io_ import AsyncWriter, Writer
    from pygls.server import JsonRPCServer

    MessageHandler = Union[Callable[[Any], Any],]
    MessageCallback = Callable[[Future[Any]], None]

logger = logging.getLogger(__name__)

# cattrs needs access to this type definition so we cannot include it in the
# TYPE_CHECKING block above
MsgId = Union[str, int]


@runtime_checkable
class RPCNotification(Protocol):
    method: str
    jsonrpc: str
    params: Any


@runtime_checkable
class RPCRequest(Protocol):
    id: MsgId
    method: str
    jsonrpc: str
    params: Any


@runtime_checkable
class RPCResponse(Protocol):
    id: MsgId
    jsonrpc: str
    result: Any


@runtime_checkable
class RPCError(Protocol):
    id: MsgId
    jsonrpc: str
    error: Any


RPCMessage = Union[RPCNotification, RPCResponse, RPCRequest, RPCError]


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

    id: MsgId
    method: str
    jsonrpc: str
    params: Any


@attrs.define
class JsonRPCResponseMessage:
    """A class that represents a generic json rpc response message.
    Used as a fallback for unknown types.
    """

    id: MsgId
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
        self._ctx_msg_id: contextvars.ContextVar[MsgId | None] = contextvars.ContextVar(
            "msg_id", default=None
        )
        self._request_futures: dict[MsgId, Future[Any]] = {}
        self._result_types: dict[MsgId, Any] = {}

        self.fm = FeatureManager(server, converter)
        self.writer: AsyncWriter | Writer | None = None
        self._include_headers = False

    def __call__(self):
        return self

    @property
    def msg_id(self) -> MsgId | None:
        """Returns the id of the current context (if it exists)."""
        ctx = contextvars.copy_context()
        return ctx.get(self._ctx_msg_id)

    def _execute_handler(
        self,
        msg_id: MsgId,
        handler: MessageHandler,
        callback: MessageCallback,
        args: tuple[Any, ...] | None = None,
        kwargs: dict[str, Any] | None = None,
    ):
        """Execute the given message handler.

        Parameters
        ----------
        msg_id
           The id of the message being handled

        handler
           The request handler to call

        callback
           An optional callback function to call upon completion of the handler

        args
           Positional arguments to pass to the handler

        kwargs
           Keyword arguments to pass to the handler
        """
        future: Future[Any]
        args = args or tuple()
        kwargs = kwargs or {}

        if asyncio.iscoroutinefunction(handler):
            future = asyncio.ensure_future(handler(*args, **kwargs))
            self._request_futures[msg_id] = future
            future.add_done_callback(callback)

        elif is_thread_function(handler):
            future = self._server.thread_pool.submit(handler, *args, **kwargs)
            self._request_futures[msg_id] = future
            future.add_done_callback(callback)

        elif inspect.isgeneratorfunction(handler):
            future = Future()
            self._request_futures[msg_id] = future
            future.add_done_callback(callback)

            try:
                self._run_generator(
                    future=None, gen=handler(*args, **kwargs), result_future=future
                )
            except Exception as exc:
                future.set_exception(exc)

        else:
            # While a future is not necessary for a synchronous function, it allows us to use a single
            # pattern across all handler types
            future = Future()
            future.add_done_callback(callback)

            try:
                result = handler(*args, **kwargs)
                future.set_result(result)
            except Exception as exc:
                future.set_exception(exc)

    def _run_generator(
        self,
        future: Future[Any] | None,
        *,
        gen: Generator[Any, Any, Any],
        result_future: Future[Any],
    ):
        """Run the next portion of the given generator.

        Generator handlers are designed to ``yield`` to other handlers that are executed
        separately before their results are sent back into the generator allowing
        execution to continue.

        Generator handlers are primarily used in the implementation of pygls' builtin
        feature handlers.

        Parameters
        ----------
        future
           The future that contains the result of the previously executed handler, if any

        gen
           The generator to run

        result_future
           The future to send the final result to once the generator stops.
        """

        if result_future.cancelled():
            return

        try:
            value = future.result() if future is not None else None
            handler, args, kwargs = gen.send(value)

            self._execute_handler(
                str(uuid.uuid4()),
                handler,
                args=args,
                kwargs=kwargs,
                callback=partial(
                    self._run_generator, gen=gen, result_future=result_future
                ),
            )
        except StopIteration as result:
            result_future.set_result(result.value)

        except Exception as exc:
            result_future.set_exception(exc)

    def _send_handler_result(self, future: Future[Any], *, msg_id: MsgId):
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
        except JsonRpcException as exc:
            logger.exception('Exception occurred for message "%s"', msg_id)
            self._send_response(msg_id, error=exc.to_response_error())
            self._server._report_server_error(exc, FeatureRequestError)

        except Exception:
            error = JsonRpcInternalError.of(sys.exc_info())
            logger.exception('Exception occurred for message "%s"', msg_id)
            self._send_response(msg_id, error=error.to_response_error())
            self._server._report_server_error(error, FeatureRequestError)

    def _check_handler_result(self, future: Future[Any]):
        """Check the result of the future to see if an error occurred.

        Used when handling notification messages
        """
        if (exc := future.exception()) is not None:
            try:
                raise exc
            except Exception:
                error = JsonRpcInternalError.of(sys.exc_info())
                self._server._report_server_error(error, FeatureNotificationError)

    def _get_handler(self, feature_name: str) -> MessageHandler:
        """Returns builtin or used defined feature by name if exists."""

        if (handler := self.fm.builtin_features.get(feature_name)) is not None:
            return handler

        if (handler := self.fm.features.get(feature_name)) is not None:
            return handler

        raise JsonRpcMethodNotFound.of(feature_name)

    def _handle_cancel_notification(self, msg_id: MsgId):
        """Handles a cancel notification from the client."""
        future = self._request_futures.pop(msg_id, None)

        if not future:
            logger.warning('Cancel notification for unknown message id "%s"', msg_id)
            return

        # Will only work if the request hasn't started executing
        if future.cancel():
            logger.info('Cancelled request with id "%s"', msg_id)

    def _handle_notification(self, method_name: str, params: Any):
        """Handles a notification from the client."""
        if method_name == CANCEL_REQUEST:
            self._handle_cancel_notification(params.id)
            return

        try:
            handler = self._get_handler(method_name)
            self._execute_handler(
                msg_id=str(uuid.uuid4()),
                handler=handler,
                args=(params,),
                callback=self._check_handler_result,
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

    def _handle_request(self, msg_id: MsgId, method_name: str, params: Any):
        """Handles a request from the client."""
        try:
            handler = self._get_handler(method_name)

            # Set the request id within the current context.
            self._ctx_msg_id.set(msg_id)
            self._execute_handler(
                msg_id=msg_id,
                handler=handler,
                args=(params,),
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

    def _handle_response(
        self,
        msg_id: MsgId,
        result: Any | None = None,
        error: ResponseError | None = None,
    ):
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

    def _serialize_message(self, data: Any) -> dict[str, Any]:
        """Function used to serialize data sent to the client."""

        if hasattr(data, "__attrs_attrs__"):
            return self._converter.unstructure(data)

        if isinstance(data, enum.Enum):
            return data.value

        return data.__dict__

    def structure_message(self, data: dict[str, Any]):
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
                        self._result_types.pop(data["id"], None)
                        or JsonRPCResponseMessage
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

    def handle_message(self, message: RPCMessage):
        """Delegates message to handlers depending on message type."""

        if message.jsonrpc != JsonRPCProtocol.VERSION:
            logger.warning('Unknown message "%s"', message)
            return

        if self._shutdown and getattr(message, "method", "") != EXIT:
            logger.warning("Server shutting down. No more requests!")
            return

        # Run each handler within its own context.
        ctx = contextvars.copy_context()

        if isinstance(message, RPCRequest):
            logger.debug("Request %r received", message.method)
            ctx.run(self._handle_request, message.id, message.method, message.params)

        elif isinstance(message, RPCNotification):
            logger.debug("Notification %r received", message.method)
            ctx.run(self._handle_notification, message.method, message.params)

        elif isinstance(message, RPCResponse):
            logger.debug("Response message received.")
            ctx.run(self._handle_response, message.id, message.result)

        else:
            logger.debug("Error message received.")
            ctx.run(self._handle_response, message.id, None, message.error)

    def _send_data(self, data: Any):
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

        except BrokenPipeError:
            logger.exception("Error sending data. BrokenPipeError", exc_info=True)
            raise
        except Exception as error:
            logger.exception("Error sending data", exc_info=True)
            self._server._report_server_error(error, JsonRpcInternalError)

    def _send_response(
        self,
        msg_id: MsgId,
        result: Any | None = None,
        error: Union[ResponseError, None] = None,
    ):
        """Send a JSON-RPC response

        .. important::

           You should only set ``result`` OR ``error``.
           If both are set, then the ``result`` value will be ignored.

        Parameters
        ----------
        msg_id
           The id of the message to respond to

        result
           The result to send in the event of a success

        error
           The error to send in the event of a failure
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

    def notify(self, method: str, params: Any | None = None):
        """Send a JSON-RPC notification.

        .. note::

           Notifications are "fire-and-forget", there is no way for the recipient to
           respond directly to a notification. If you expect a response to this message,
           use ``send_request``.

        Parameters
        ----------
        method
           The method name of the message to send

        params
           The payload of the message

        """
        logger.debug("Sending notification: '%s' %s", method, params)

        notification_type = self.get_message_type(method) or JsonRPCNotification
        notification = notification_type(
            method=method, params=params, jsonrpc=JsonRPCProtocol.VERSION
        )

        self._send_data(notification)

    def send_request(
        self,
        method: str,
        params: Any | None = None,
        callback: Callable[[Any], None] | None = None,
        msg_id: MsgId | None = None,
    ) -> Future[Any]:
        """Send a JSON-RPC request

        Parameters
        ----------
        method
           The method name of the message to send

        params
           The payload of the message

        callback
           If set, the given callback will be called with the result of the future
           when it resolves

        msg_id
           Send the request using the given id, if ``None``, an id will be automatically
           generated

        Returns
        -------
        Future[Any]
           A future that will resolve once a response has been received
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

        future: Future[Any] = Future()
        # If callback function is given, call it when result is received
        if callback:

            def wrapper(fut: Future[Any]):
                result = fut.result()
                logger.info("Client response for %s received: %s", params, result)
                callback(result)

            future.add_done_callback(wrapper)

        self._request_futures[msg_id] = future
        self._result_types[msg_id] = self.get_result_type(method)

        self._send_data(request)

        return future

    def send_request_async(
        self, method: str, params: Any | None = None, msg_id: MsgId | None = None
    ):
        """Send a JSON-RPC request, asynchronously.

        This method calls `send_request`, wrapping the resulting future with
        ``asyncio.wrap_future`` so it can be used in an ``async def`` function and
        awaited with the ``await`` keyword.

        Parameters
        ----------
        method
           The method name of the message to send

        params
           The payload of the message

        callback
           If set, the given callback will be called with the result of the future
           when it resolves

        msg_id
           Send the request using the given id, if ``None``, an id will be automatically
           generated

        Returns
        -------
        `asyncio.Future` that can be awaited
        """
        return asyncio.wrap_future(
            self.send_request(method, params=params, msg_id=msg_id)
        )
