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
import logging
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from re import findall
from threading import Event
from typing import Any, Callable, Dict, List, Optional

from pygls.types import (ApplyWorkspaceEditResponse, ConfigCallbackType,
                         MessageType, WorkspaceEdit)

from . import IS_WIN
from .protocol import LanguageServerProtocol
from .types import ConfigurationParams
from .workspace import Workspace

logger = logging.getLogger(__name__)


async def aio_readline(loop, executor, stop_event, rfile, proxy):
    """Reads data from stdin in separate thread (asynchronously)."""
    while not stop_event.is_set():
        # Read line
        line = await loop.run_in_executor(executor, rfile.readline)

        if not line:
            continue

        # Extract content length from line
        try:
            content_length = int(findall(rb'\b\d+\b', line)[0])
            logger.debug('Content length: {}'.format(content_length))
        except IndexError:
            continue

        # Throw away empty lines
        while line and line.strip():
            line = await loop.run_in_executor(executor, rfile.readline)

        if not line:
            continue

        # Read body
        body = await loop.run_in_executor(executor, rfile.read, content_length)

        # Pass body to language server protocol
        if body:
            proxy(body)


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


class Server:
    """Class that represents async server. It can be started using TCP or IO.

    Args:
        protocol_cls(Protocol): Protocol implementation that must be derived
                                from `asyncio.Protocol`
        max_workers(int, optional): Number of workers for `ThreadPool` and
                                    `ThreadPoolExecutor`

    Attributes:
        _max_workers(int): Number of workers for thread pool executor
        _server(Server): Server object which can be used to stop the process
        _stop_event(Event): Event used for stopping `aio_readline`
        _thread_pool(ThreadPool): Thread pool for executing methods decorated
                                  with `@ls.thread()` - lazy instantiated
        _thread_pool_executor(ThreadPoolExecutor): Thread pool executor
                                                   passed to `run_in_executor`
                                                    - lazy instantiated
    """

    def __init__(self, protocol_cls, loop=None, max_workers=2):
        assert issubclass(protocol_cls, asyncio.Protocol)

        self._max_workers = max_workers
        self._server = None
        self._stop_event = None
        self._thread_pool = None
        self._thread_pool_executor = None

        if IS_WIN:
            asyncio.set_event_loop(asyncio.ProactorEventLoop())
        else:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())

        self.loop = loop or asyncio.get_event_loop()

        try:
            asyncio.get_child_watcher().attach_loop(self.loop)
        except NotImplementedError:
            pass

        self.lsp = protocol_cls(self)

    def shutdown(self):
        """Shutdown server."""
        logger.info('Shutting down the server')

        if self._thread_pool:
            self._thread_pool.terminate()
            self._thread_pool.join()

        if self._thread_pool_executor:
            self._thread_pool_executor.shutdown()

        if self._server:
            self._server.close()
            self.loop.run_until_complete(self._server.wait_closed())

        logger.info('Closing the event loop.')
        self.loop.close()

    def start_io(self, stdin=None, stdout=None):
        """Starts IO server."""
        logger.info('Starting IO server')

        self._stop_event = Event()
        transport = StdOutTransportAdapter(stdin or sys.stdin.buffer,
                                           stdout or sys.stdout.buffer)
        self.lsp.connection_made(transport)

        try:
            self.loop.run_until_complete(
                aio_readline(self.loop,
                             self.thread_pool_executor,
                             self._stop_event,
                             stdin or sys.stdin.buffer,
                             self.lsp.data_received))
        except SystemExit:
            pass
        finally:
            self._stop_event.set()
            self.shutdown()

    def start_tcp(self, host, port):
        """Starts TCP server."""
        logger.info('Starting server on {}:{}'.format(host, port))

        self._server = self.loop.run_until_complete(
            self.loop.create_server(self.lsp, host, port)
        )
        try:
            self.loop.run_forever()
        except SystemExit:
            pass
        finally:
            self.shutdown()

    @property
    def thread_pool(self) -> ThreadPool:
        """Returns thread pool instance (lazy initialization)."""
        if not self._thread_pool:
            self._thread_pool = ThreadPool(processes=self._max_workers)

        return self._thread_pool

    @property
    def thread_pool_executor(self) -> ThreadPoolExecutor:
        """Returns thread pool instance (lazy initialization)."""
        if not self._thread_pool_executor:
            self._thread_pool_executor = \
                ThreadPoolExecutor(max_workers=self._max_workers)

        return self._thread_pool_executor


class LanguageServer(Server):
    """A class that represents Language server using Language Server Protocol.

    This class can be extended and it can be passed as a first argument to
    registered commands/features.

    Args:
        protocol_cls(LanguageServerProtocol): LSP or any subclass of it
        max_workers(int, optional): Number of workers for `ThreadPool` and
                                    `ThreadPoolExecutor`
    """

    def __init__(self, loop=None, protocol_cls=LanguageServerProtocol, max_workers: int = 2):
        assert issubclass(protocol_cls, LanguageServerProtocol)
        super().__init__(LanguageServerProtocol, loop, max_workers)

    def apply_edit(self, edit: WorkspaceEdit, label: str = None) -> ApplyWorkspaceEditResponse:
        """Sends apply edit request to the client."""
        return self.lsp.apply_edit(edit, label)

    def command(self, command_name: str) -> Callable:
        """Decorator used to register custom commands.

        Example:
            @ls.command('myCustomCommand')
            def my_cmd(ls, a, b, c):
                pass
        """
        return self.lsp.fm.command(command_name)

    def feature(self, feature_name: str, **options: Dict) -> Callable:
        """Decorator used to register LSP features.

        Example:
            @ls.feature('textDocument/completion', triggerCharacters=['.'])
            def completions(ls, params: CompletionRequest):
                return CompletionList(False, [CompletionItem("Completion 1")])
        """
        return self.lsp.fm.feature(feature_name, **options)

    def get_configuration(self, params: ConfigurationParams,
                          callback: ConfigCallbackType = None) -> Future:
        """Gets the configuration settings from the client."""
        return self.lsp.get_configuration(params, callback)

    def get_configuration_async(self, params: ConfigurationParams) -> asyncio.Future:
        """Gets the configuration settings from the client."""
        return self.lsp.get_configuration_async(params)

    def send_notification(self, method: str, params: object = None) -> None:
        """Sends notification to the client."""
        self.lsp.notify(method, params)

    def show_message(self, message, msg_type=MessageType.Info) -> None:
        """Sends message to the client to display message."""
        self.lsp.show_message(message, msg_type)

    def show_message_log(self, message, msg_type=MessageType.Log) -> None:
        """Sends message to the client's output channel."""
        self.lsp.show_message_log(message, msg_type)

    def thread(self) -> Callable:
        """Decorator that mark function to execute it in a thread."""
        return self.lsp.thread()

    @property
    def workspace(self) -> Workspace:
        """Returns in-memory workspace."""
        return self.lsp.workspace
