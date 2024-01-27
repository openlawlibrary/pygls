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
from typing import Optional
from typing import Type

from pygls.protocol import JsonRPCHandler
from pygls.protocol import JsonRPCProtocol
from pygls.protocol import rpc_main_loop

_CLIENT_SERVER_CONNECTION = "<<client-server-connection>>"
_EXIT_NOTIFICATION = "<<exit-notification>>"


class JsonRPCClient(JsonRPCHandler):
    """Base JSON-RPC client for "native" runtimes"""

    def __init__(
        self, *, protocol_cls: Type[JsonRPCProtocol] = JsonRPCProtocol, **kwargs
    ):
        super().__init__(protocol=protocol_cls(), **kwargs)

        self._server: Optional[asyncio.subprocess.Process] = None

    @property
    def stopped(self) -> bool:
        """Return ``True`` if the client has been stopped."""
        return self._stop_event.is_set()

    async def start_io(self, cmd: str, *args, **kwargs):
        """Start the given server and communicate with it over stdio."""

        self.logger.debug("Starting server process: %s", " ".join([cmd, *args]))
        server = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )

        assert server.stdout is not None, "Missing server stdout"
        assert server.stdin is not None, "Missing server stdin"

        self._writer = server.stdin
        self._create_task(
            rpc_main_loop(
                reader=server.stdout,
                stop_event=self._stop_event,
                message_handler=self,
            ),
            task_id=_CLIENT_SERVER_CONNECTION,
        )
        self._create_task(self._server_exit(server), task_id=_EXIT_NOTIFICATION)
        self._server = server

    async def _server_exit(self, server: asyncio.subprocess.Process):
        """Internal server exit handler to ensure that the client responds to the server
        process disappearing."""

        await server.wait()
        server_pid = server.pid
        server_exit_code = server.returncode

        self.logger.debug(
            "Server process %s exited with return code: %s",
            server_pid,
            server_exit_code,
        )

        # Cancel pending tasks
        for task_id, task in self._tasks.items():
            if task_id not in {_EXIT_NOTIFICATION, _CLIENT_SERVER_CONNECTION}:
                task.cancel(
                    f"Server process {server_pid} exited with "
                    f"return code: {server_exit_code}"
                )

        # Notify the user's code that the server has stopped.
        try:
            await self.server_exit(server)
        except Exception as exc:
            self.logger.error("Error in 'server_exit' handler", exc_info=True)
            self._error_handler(exc)

        self._stop_event.set()

    async def server_exit(self, server: asyncio.subprocess.Process):
        """Called when the server process exits."""

    async def stop(self):
        self._stop_event.set()

        # Give any remaining tasks an opportunity to finish
        await asyncio.sleep(0.1)

        # Cancel pending tasks
        for task_id, task in self._tasks.items():
            if task_id not in {_EXIT_NOTIFICATION, _CLIENT_SERVER_CONNECTION}:
                task.cancel("Client is stopping")

        # Kill the server process
        if self._server is not None and self._server.returncode is None:
            self.logger.debug("Terminating server process: %s", self._server.pid)
            self._server.terminate()

        # Wait for the remaining tasks
        if len(self._tasks) > 0:
            self.logger.debug(self._tasks.keys())
            await asyncio.gather(*self._tasks.values())
