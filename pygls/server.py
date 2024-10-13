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
import json
import logging
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any, BinaryIO, Callable, Optional, Type, TypeVar, Union

import cattrs
from pygls.exceptions import (
    FeatureNotificationError,
    JsonRpcInternalError,
    PyglsError,
    JsonRpcException,
    FeatureRequestError,
)
from pygls.protocol import JsonRPCProtocol


logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)

ServerErrors = Union[
    PyglsError,
    JsonRpcException,
    Type[JsonRpcInternalError],
    Type[FeatureNotificationError],
    Type[FeatureRequestError],
]


async def aio_readline(loop, executor, stop_event, rfile, proxy):
    """Reads data from stdin in separate thread (asynchronously)."""

    CONTENT_LENGTH_PATTERN = re.compile(rb"^Content-Length: (\d+)\r\n$")

    # Initialize message buffer
    message = []
    content_length = 0

    while not stop_event.is_set() and not rfile.closed:
        # Read a header line
        header = await loop.run_in_executor(executor, rfile.readline)
        if not header:
            break
        message.append(header)

        # Extract content length if possible
        if not content_length:
            match = CONTENT_LENGTH_PATTERN.fullmatch(header)
            if match:
                content_length = int(match.group(1))
                logger.debug("Content length: %s", content_length)

        # Check if all headers have been read (as indicated by an empty line \r\n)
        if content_length and not header.strip():
            # Read body
            body = await loop.run_in_executor(executor, rfile.read, content_length)
            if not body:
                break
            message.append(body)

            # Pass message to language server protocol
            proxy(b"".join(message))

            # Reset the buffer
            message = []
            content_length = 0


class StdOutTransportAdapter:
    """Protocol adapter which overrides write method.

    Write method sends data to stdout.
    """

    def __init__(self, rfile, wfile):
        self.rfile = rfile
        self.wfile = wfile

    def close(self):
        self.rfile.close()
        self.wfile.close()

    def write(self, data):
        self.wfile.write(data)
        self.wfile.flush()


class PyodideTransportAdapter:
    """Protocol adapter which overrides write method.

    Write method sends data to stdout.
    """

    def __init__(self, wfile):
        self.wfile = wfile

    def close(self):
        self.wfile.close()

    def write(self, data):
        self.wfile.write(data)
        self.wfile.flush()


class WebSocketTransportAdapter:
    """Protocol adapter which calls write method.

    Write method sends data via the WebSocket interface.
    """

    def __init__(self, ws):
        self._ws = ws

    def close(self) -> None:
        """Stop the WebSocket server."""
        asyncio.ensure_future(self._ws.close())

    def write(self, data: Any) -> None:
        """Create a task to write specified data into a WebSocket."""
        asyncio.ensure_future(self._ws.send(data))


class JsonRPCServer:
    """Base server class

    Parameters
    ----------
    protocol_cls
       Protocol implementation that must be derive from :class:`~pygls.protocol.JsonRPCProtocol`

    converter_factory
       Factory function to use when constructing a cattrs converter.

    loop
       The asyncio event loop

    max_workers
       Maximum number of workers for `ThreadPoolExecutor`

    """

    protocol: JsonRPCProtocol

    def __init__(
        self,
        protocol_cls: Type[JsonRPCProtocol],
        converter_factory: Callable[[], cattrs.Converter],
        loop: asyncio.AbstractEventLoop | None = None,
        max_workers: int | None = None,
    ):
        if not issubclass(protocol_cls, asyncio.Protocol):
            raise TypeError("Protocol class should be subclass of asyncio.Protocol")

        self._max_workers = max_workers
        self._server = None
        self._stop_event: Event | None = None
        self._thread_pool: ThreadPoolExecutor | None = None

        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._owns_loop = True
        else:
            self._owns_loop = False

        self.loop = loop
        self.protocol = protocol_cls(self, converter_factory())

    def shutdown(self):
        """Shutdown server."""
        logger.info("Shutting down the server")

        if self._stop_event is not None:
            self._stop_event.set()

        if self._thread_pool:
            self._thread_pool.shutdown()

        if self._server:
            self._server.close()
            self.loop.run_until_complete(self._server.wait_closed())

        if self._owns_loop and not self.loop.is_closed():
            logger.info("Closing the event loop.")
            self.loop.close()

    def _report_server_error(
        self,
        error: Exception,
        source: ServerErrors,
    ):
        # Prevent recursive error reporting
        try:
            self.report_server_error(error, source)
        except Exception:
            logger.warning("Failed to report error")

    def report_server_error(self, error: Exception, source: ServerErrors):
        """Default error reporter."""
        logger.error("%s", error)

    def start_io(
        self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None
    ):
        """Starts IO server."""
        logger.info("Starting IO server")

        self._stop_event = Event()
        transport = StdOutTransportAdapter(
            stdin or sys.stdin.buffer, stdout or sys.stdout.buffer
        )
        self.protocol.connection_made(transport)  # type: ignore[arg-type]

        try:
            self.loop.run_until_complete(
                aio_readline(
                    self.loop,
                    self.thread_pool,
                    self._stop_event,
                    stdin or sys.stdin.buffer,
                    self.protocol.data_received,
                )
            )
        except BrokenPipeError:
            logger.error("Connection to the client is lost! Shutting down the server.")
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.shutdown()

    def start_pyodide(self):
        logger.info("Starting Pyodide server")

        # Note: We don't actually start anything running as the main event
        # loop will be handled by the web platform.
        transport = PyodideTransportAdapter(sys.stdout)
        self.protocol.connection_made(transport)  # type: ignore[arg-type]
        self.protocol._send_only_body = True  # Don't send headers within the payload

    def start_tcp(self, host: str, port: int) -> None:
        """Starts TCP server."""
        logger.info("Starting TCP server on %s:%s", host, port)

        self._stop_event = Event()
        self._server = self.loop.run_until_complete(  # type: ignore[assignment]
            self.loop.create_server(self.protocol, host, port)
        )
        try:
            self.loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.shutdown()

    def start_ws(self, host: str, port: int) -> None:
        """Starts WebSocket server."""
        try:
            from websockets.server import serve
        except ImportError:
            logger.error("Run `pip install pygls[ws]` to install `websockets`.")
            sys.exit(1)

        logger.info("Starting WebSocket server on {}:{}".format(host, port))

        self._stop_event = Event()
        self.protocol._send_only_body = True  # Don't send headers within the payload

        async def connection_made(websocket, _):
            """Handle new connection wrapped in the WebSocket."""
            self.protocol.transport = WebSocketTransportAdapter(websocket)
            async for message in websocket:
                self.protocol.handle_message(
                    json.loads(message, object_hook=self.protocol.structure_message)
                )

        start_server = serve(connection_made, host, port, loop=self.loop)
        self._server = start_server.ws_server  # type: ignore[assignment]
        self.loop.run_until_complete(start_server)

        try:
            self.loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self._stop_event.set()
            self.shutdown()

    def command(self, command_name: str) -> Callable[[F], F]:
        """Decorator used to register custom commands.

        Example
        -------
        ::

           @ls.command('myCustomCommand')
           def my_cmd(ls, a, b, c):
               pass
        """
        return self.protocol.fm.command(command_name)

    def thread(self) -> Callable[[F], F]:
        """Decorator that mark function to execute it in a thread."""
        return self.protocol.fm.thread()

    def feature(
        self,
        feature_name: str,
        options: Any | None = None,
    ) -> Callable[[F], F]:
        """Decorator used to register LSP features.

        Example
        -------
        ::

           @ls.feature('textDocument/completion', CompletionOptions(trigger_characters=['.']))
           def completions(ls, params: CompletionParams):
               return CompletionList(is_incomplete=False, items=[CompletionItem("Completion 1")])
        """
        return self.protocol.fm.feature(feature_name, options)

    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        """Returns thread pool instance (lazy initialization)."""
        if not self._thread_pool:
            self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)

        return self._thread_pool
