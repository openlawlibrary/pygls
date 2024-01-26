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

import inspect
import logging
import re
import sys
import threading
import typing
from concurrent.futures import Future
from functools import partial

from pygls.exceptions import JsonRpcException
from pygls.exceptions import JsonRpcInternalError
from pygls.exceptions import JsonRpcMethodNotFound

from . import json_rpc
from ._features import FeatureManager

if typing.TYPE_CHECKING:
    import io
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Optional
    from typing import TypeVar

    import cattrs

    MessageHandler = Callable[[bytes], None]
    T = TypeVar("T")


CONTENT_LENGTH_PATTERN = re.compile(rb"^Content-Length: (\d+)\r\n$")


class JsonRPCHandler:
    """JSON-RPC message handler with no asyncio capability.

    This is primarily useful for WebAssembly runtimes where asyncio etc. are not
    available
    """

    def __init__(
        self,
        *,
        protocol: json_rpc.JsonRPCProtocol,
        logger: Optional[logging.Logger] = None,
    ):
        self.protocol = protocol
        self.logger = logger or logging.getLogger(__name__)

        self._stop_event = threading.Event()
        self._include_headers = True
        self._writer: Optional[io.BufferedWriter] = None
        self._features = FeatureManager(self.converter, self.logger)

        self._futures: Dict[json_rpc.MsgId, Future[Any]] = {}

    def __call__(self, data: bytes) -> Any:
        try:
            message = self.protocol.decode_message(data)
        except JsonRpcException as exc:
            self._error_handler(exc)
            return

        if isinstance(message, json_rpc.JsonRPCRequestMessage):
            self._handle_request(message.id, message.method, message.params)

        elif isinstance(message, json_rpc.JsonRPCNotification):
            self._handle_notification(message.method, message.params)

        elif isinstance(message, json_rpc.JsonRPCResultMessage):
            self._handle_result(message.id, message.result)

        else:
            self._handle_error(message.id, message.error)

    @property
    def converter(self) -> cattrs.Converter:
        return self.protocol.converter

    @property
    def writer(self) -> io.BufferedWriter:
        if self._writer is None:
            raise RuntimeError("Unable to send data, writer not available!")

        return self._writer

    def _get_handler(self, method: str):
        return self._features.builtin_features.get(
            method, self._features.user_features.get(method, None)
        )

    def _send(self, data: bytes):
        self.writer.write(data)
        self.writer.flush()

    def send_error(self, msg_id: json_rpc.MsgId, error: Any):
        """Send an error message."""
        message = self.protocol.encode_error(msg_id, error, self._include_headers)
        self._send(message)

    def send_notification(self, method: str, params: Any):
        """Send a notification message."""
        message = self.protocol.encode_notification(
            method, params, self._include_headers
        )
        self._send(message)

    def send_result(self, msg_id: json_rpc.MsgId, result: Any):
        """Send a result message."""
        message = self.protocol.encode_result(msg_id, result, self._include_headers)
        self._send(message)

    def send_request(
        self,
        method: str,
        params: Any,
        msg_id: Optional[json_rpc.MsgId] = None,
        callback: Optional[Callable[[Any], None]] = None,
    ) -> Future[Any]:
        """Send a request message.

        Parameters
        ----------
        method
           The request method name

        params
           The request parameters

        msg_id
           The message id, if not set, an id will be generated automatically

        callback
           If set, will be called with the request's result

        Returns
        -------
        Future[Any]
           A future which, when complete, will contain the request's result.
        """

        msg_id = msg_id or self.protocol.make_id()
        message = self.protocol.encode_request(method, params=params, msg_id=msg_id)

        fut = Future()
        self._futures[msg_id] = fut

        self._send(message)

        if callback:
            fut.add_done_callback(partial(_unwrap_future, callback))

        return fut

    def _execute_handler(self, handler, *args, **kwargs):
        """Execute the given handler with the given arguments."""

        # Call the handler.
        result: Any = handler(*args, **kwargs)

        # Some may be generators
        if inspect.isgenerator(result):
            result = self._run_generator(result)

        return result

    def _run_generator(self, gen):
        """Run the given generator.

        Generators may ``yield`` additional handlers to call, which is how pygls'
        builtin handlers may call out to user defined handlers.
        """
        result = None
        try:
            while True:
                result = gen.send(result)
                if isinstance(result, tuple) and callable(result[0]):
                    result = self._execute_handler(result[0], *result[1], **result[2])
        except StopIteration as exc:
            result = exc.value

        return result

    def _handle_request(self, msg_id: json_rpc.MsgId, method: str, params: Any):
        """Handle a JSON-RPC request message.

        Parameters
        ----------
        msg_id
           The message id.

        method
           The method name

        params
           The request parameters
        """
        if (handler := self._get_handler(method)) is None:
            error = JsonRpcMethodNotFound.of(method)
            self.send_error(msg_id, error.to_response_error())
            return

        try:
            result = self._execute_handler(handler, params)
        except JsonRpcException as exc:
            # Allow handlers to raise their own errors
            self.send_error(msg_id, exc.to_response_error())
            return

        except Exception:
            self.logger.error("Error handling '%s' request", method, exc_info=True)

            exc = JsonRpcInternalError.of(sys.exc_info())
            self.send_error(msg_id, exc.to_response_error())
            return

        self.send_result(msg_id, result)

    def _handle_notification(self, method: str, params: Any):
        """Handle a JSON-RPC notification message.

        Parameters
        ----------
        method
           The method name

        params
           The message parameters
        """
        if (handler := self._get_handler(method)) is None:
            self.logger.warning("Ignoring unknown notififcation: '%s'", method)
            return

        try:
            self._execute_handler(handler, params)
        except Exception as exc:
            # There is no mechanism to send an error in response to a notification
            self.logger.error("Error handling '%s' notification", method, exc_info=True)
            self._error_handler(exc)

    def _handle_result(self, msg_id: json_rpc.MsgId, result: Any):
        """Handle a JSON-RPC result message.

        Parameters
        ----------
        msg_id
           The message id

        result
           The result
        """
        if msg_id not in self._futures:
            self.logger.error("Received result for unknown message '%s'", msg_id)
            return

        self._futures[msg_id].set_result(result)

    def _handle_error(self, msg_id: json_rpc.MsgId, error: Any):
        """Handle a JSON-RPC error message.

        Parameters
        ----------
        msg_id
           The message id

        error
           The error
        """
        if msg_id not in self._futures:
            self.logger.error(
                "Received error response for unknown message '%s'", msg_id
            )
            return

        exc = JsonRpcException.from_error(error)
        self._futures[msg_id].set_exception(exc)

    def error_handler(self, exc: Exception):
        """Override to customize error handling"""
        self.logger.error("%s", exc, exc_info=True)

    def _error_handler(self, exc: Exception):
        try:
            self.error_handler(exc)
        except Exception:
            self.logger.error("There was an error handling an error!!", exc_info=True)

    def feature(
        self,
        feature_name: str,
        options: Optional[Any] = None,
        **kwargs,
    ):
        """Decorator used to register features.

        Example
        -------
        ::

           import logging
           from pygls.client import JsonRPCClient

           ls = JsonRPCClient()

           @ls.feature('window/logMessage')
           def completions(ls, params):
               logging.info("%s", params.message)
        """
        return self._features.feature(self, feature_name, options, **kwargs)


def _unwrap_future(callback: Callable[[Any], None], future: Future[Any]):
    """Call the given callback with the future's result."""
    callback(future.result())


def rpc_main_loop(
    reader: io.BufferedReader,
    stop_event: threading.Event,
    message_handler: MessageHandler,
):
    """Main loop."""

    content_length = 0

    while not stop_event.is_set():
        # Read a header line
        header = reader.readline()
        if not header:
            break

        # Extract content length if possible
        if not content_length:
            match = CONTENT_LENGTH_PATTERN.fullmatch(header)
            if match:
                content_length = int(match.group(1))

        # Check if all headers have been read (as indicated by an empty line \r\n)
        if content_length and not header.strip():
            # Read body
            body = reader.read(content_length)
            if not body:
                break

            message_handler(body)
            content_length = 0
