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
from threading import Event

from pygls.exceptions import JsonRpcException, PyglsError
from pygls.io_ import run_async, run_websocket
from pygls.protocol import JsonRPCProtocol, default_converter

if typing.TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import List
    from typing import Optional
    from typing import Type

    from cattrs import Converter

logger = logging.getLogger(__name__)


class JsonRPCClient:
    """Base JSON-RPC client."""

    def __init__(
        self,
        protocol_cls: Type[JsonRPCProtocol] = JsonRPCProtocol,
        converter_factory: Callable[[], Converter] = default_converter,
    ):
        # Strictly speaking, `JsonRPCProtocol` wants a `JsonRPCServer`, not a
        # `JsonRPCClient`. However they're similar enough for our purposes, which
        # is that this client will mostly be used in testing contexts.
        self.protocol = protocol_cls(self, converter_factory())  # type: ignore

        self._server: Optional[asyncio.subprocess.Process] = None
        self._stop_event = Event()
        self._async_tasks: List[asyncio.Task[Any]] = []

    @property
    def stopped(self) -> bool:
        """Return ``True`` if the client has been stopped."""
        return self._stop_event.is_set()

    def feature(
        self,
        feature_name: str,
        options: Optional[Any] = None,
    ):
        """Decorator used to register LSP features.

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
        return self.protocol.fm.feature(feature_name, options)

    async def start_io(self, cmd: str, *args, **kwargs):
        """Start the given server and communicate with it over stdio."""

        logger.debug("Starting server process: %s", " ".join([cmd, *args]))
        server = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )

        # Keep mypy happy
        if server.stdout is None:
            raise RuntimeError("Server process is missing a stdout stream")

        # Keep mypy happy
        if server.stdin is None:
            raise RuntimeError("Server process is missing a stdin stream")

        self.protocol.set_writer(server.stdin)
        connection = asyncio.create_task(
            run_async(
                stop_event=self._stop_event,
                reader=server.stdout,
                protocol=self.protocol,
                logger=logger,
                error_handler=self.report_server_error,
            )
        )
        notify_exit = asyncio.create_task(self._server_exit())

        self._server = server
        self._async_tasks.extend([connection, notify_exit])

    async def start_tcp(self, host: str, port: int):
        """Start communicating with a server over TCP."""
        reader, writer = await asyncio.open_connection(host, port)

        self.protocol.set_writer(writer)
        connection = asyncio.create_task(
            run_async(
                stop_event=self._stop_event,
                reader=reader,
                protocol=self.protocol,
                logger=logger,
                error_handler=self.report_server_error,
            )
        )

        self._async_tasks.extend([connection])

    async def start_ws(self, host: str, port: int):
        """Start communicating with a server over WebSockets."""

        try:
            from websockets.asyncio.client import connect
        except ImportError:
            logger.exception(
                "Run `pip install pygls[ws]` to install dependencies required for websockets."
            )
            sys.exit(1)

        uri = f"ws://{host}:{port}"
        websocket = await connect(uri)
        connection = asyncio.create_task(
            run_websocket(
                stop_event=self._stop_event,
                websocket=websocket,
                protocol=self.protocol,
                logger=logger,
                error_handler=self.report_server_error,
            )
        )
        self._async_tasks.extend([connection])

        # Yield control to the event loop, gives the run_websocket task chance to spin up.
        await asyncio.sleep(0)

    async def _server_exit(self):
        """Cleanup handler that runs when the server process managed by the client exits"""
        if self._server is None:
            return

        await self._server.wait()

        pid = self._server.pid
        returncode = self._server.returncode

        reason = f"Server process {pid} exited with return code: {returncode}"
        logger.debug(reason)

        # Cancel any pending requests
        for id_, fut in self.protocol._request_futures.items():
            if not fut.done():
                fut.set_exception(RuntimeError(reason))
                logger.debug("Cancelled pending request '%s': %s", id_, reason)

        try:
            await self.server_exit(self._server)
        except Exception:
            logger.exception("Error in server_exit handler")

        self._stop_event.set()

    async def server_exit(self, server: asyncio.subprocess.Process):
        """Called when the server process exits."""

    def _report_server_error(
        self, error: Exception, source: type[PyglsError] | type[JsonRpcException]
    ):
        try:
            self.report_server_error(error, source)
        except Exception:
            logger.exception("Unable to report error")

    def report_server_error(
        self, error: Exception, source: type[PyglsError] | type[JsonRpcException]
    ):
        """Called when the server does something unexpected e.g. respond with malformed
        JSON."""

    async def stop(self):
        self._stop_event.set()

        if self._server is not None and self._server.returncode is None:
            await self._server.wait()

        if len(self._async_tasks) > 0:
            await asyncio.gather(*self._async_tasks)
