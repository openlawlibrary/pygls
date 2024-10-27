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
import logging
import sys
import typing
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import cattrs

from pygls import IS_WASM
from pygls.exceptions import JsonRpcException, PyglsError
from pygls.io_ import StdinAsyncReader, StdoutWriter, run, run_async, run_websocket
from pygls.protocol import JsonRPCProtocol

if typing.TYPE_CHECKING:
    from typing import Any, BinaryIO, Callable, Optional, Type, TypeVar, Union

    from websockets.asyncio.server import Server as WSServer
    from websockets.asyncio.server import ServerConnection

    F = TypeVar("F", bound=Callable)
    ServerErrors = Union[type[PyglsError], type[JsonRpcException]]


logger = logging.getLogger(__name__)


class JsonRPCServer:
    """Base server class

    Parameters
    ----------
    protocol_cls
       Protocol implementation that should derive from
       :class:`~pygls.protocol.JsonRPCProtocol`

    converter_factory
       Factory function to use when constructing a cattrs converter.

    max_workers
       Maximum number of workers for `ThreadPoolExecutor`

    """

    protocol: JsonRPCProtocol

    def __init__(
        self,
        protocol_cls: Type[JsonRPCProtocol],
        converter_factory: Callable[[], cattrs.Converter],
        max_workers: int | None = None,
    ):
        self._max_workers = max_workers
        self._server: asyncio.Server | WSServer | None = None
        self._stop_event: Event | None = None
        self._thread_pool: ThreadPoolExecutor | None = None

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
        """Starts an IO server."""

        if IS_WASM:
            self._start_io_sync(stdin, stdout)
        else:
            self._start_io_async(stdin, stdout)

    def _start_io_async(
        self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None
    ):
        """Starts an asynchronous IO server."""
        logger.info("Starting async IO server")

        self._stop_event = Event()
        reader = StdinAsyncReader(stdin or sys.stdin.buffer, self.thread_pool)
        writer = StdoutWriter(stdout or sys.stdout.buffer)
        self.protocol.set_writer(writer)

        try:
            asyncio.run(
                run_async(
                    stop_event=self._stop_event,
                    reader=reader,
                    protocol=self.protocol,
                    logger=logger,
                    error_handler=self.report_server_error,
                )
            )
        except BrokenPipeError:
            logger.error("Connection to the client is lost! Shutting down the server.")
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.shutdown()

    def _start_io_sync(
        self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None
    ):
        """Starts an synchronous IO server."""
        logger.info("Starting sync IO server")

        self._stop_event = Event()
        writer = StdoutWriter(stdout or sys.stdout.buffer)
        self.protocol.set_writer(writer)

        try:
            asyncio.run(
                run(
                    stop_event=self._stop_event,
                    reader=stdin or sys.stdin.buffer,
                    protocol=self.protocol,
                    logger=logger,
                    error_handler=self.report_server_error,
                )
            )
        except BrokenPipeError:
            logger.error("Connection to the client is lost! Shutting down the server.")
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.shutdown()

    def start_tcp(self, host: str, port: int) -> None:
        """Starts TCP server."""
        logger.info("Starting TCP server on %s:%s", host, port)

        self._stop_event = stop_event = Event()

        async def lsp_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ):
            logger.debug("Connected to client")
            self.protocol.set_writer(writer)  # type: ignore
            await run_async(
                stop_event=stop_event,
                reader=reader,
                protocol=self.protocol,
                logger=logger,
                error_handler=self.report_server_error,
            )
            logger.debug("Main loop finished")
            self.shutdown()

        async def tcp_server(h: str, p: int):
            self._server = await asyncio.start_server(lsp_connection, h, p)

            addrs = ", ".join(str(sock.getsockname()) for sock in self._server.sockets)
            logger.info(f"Serving on {addrs}")

            async with self._server:
                await self._server.serve_forever()

        try:
            asyncio.run(tcp_server(host, port))
        except asyncio.CancelledError:
            logger.debug("Server was cancelled")

    def start_ws(self, host: str, port: int) -> None:
        """Starts WebSocket server."""
        try:
            from websockets.asyncio.server import serve
        except ImportError:
            logger.error(
                "Run `pip install pygls[ws]` to install dependencies required for websockets."
            )
            sys.exit(1)

        logger.info("Starting WebSocket server on {}:{}".format(host, port))
        self._stop_event = stop_event = Event()

        async def lsp_connection(websocket: ServerConnection):
            await run_websocket(
                stop_event=stop_event,
                websocket=websocket,
                protocol=self.protocol,
                logger=logger,
                error_handler=self.report_server_error,
            )
            self.shutdown()

        async def ws_server(h: str, p: int):
            self._server = await serve(lsp_connection, host, port)

            addrs = ", ".join(str(sock.getsockname()) for sock in self._server.sockets)
            logger.info(f"Serving on {addrs}")

            async with self._server:
                await self._server.serve_forever()

        try:
            asyncio.run(ws_server(host, port))
        except asyncio.CancelledError:
            logger.debug("Server was cancelled")

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
