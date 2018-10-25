import asyncio
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
from re import findall
from threading import Event

from . import IS_WIN
from .protocol import LanguageServerProtocol

logger = logging.getLogger(__name__)


async def aio_readline(loop, executor, stop_event, rfile, proxy):
    '''
    Read data from stdin in separate thread (asynchronously)
    '''
    while not stop_event.is_set():
        # Read line
        line = await loop.run_in_executor(executor, rfile.readline)

        if not line:
            continue

        # Extract content length from line
        try:
            content_length = int(findall(rb'\b\d+\b', line)[0])
            logger.info(content_length)
        except:
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


class StdOutTransportAdapter(asyncio.Transport):
    '''
    Protocol adapter which overrides write method.
    Write method sends data to stdout.
    '''

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
    def __init__(self, protocol_cls, max_workers=2):
        assert issubclass(protocol_cls, asyncio.Protocol)
        self._max_workers = max_workers
        self._server = None
        self._stop_event = Event()
        self._task = None
        self._thread_pool = None
        self._thread_pool_executor = None

        if IS_WIN:
            asyncio.set_event_loop(asyncio.ProactorEventLoop())

        self.loop = asyncio.new_event_loop()

        self.lsp = protocol_cls(self)

    @property
    def thread_pool(self):
        '''
        Returns thread pool instance (lazy initialization)
        '''
        # TODO: Specify number of processes
        if not self._thread_pool:
            self._thread_pool = ThreadPool(processes=self._max_workers)

        return self._thread_pool

    @property
    def thread_pool_executor(self):
        '''
        Returns thread pool instance (lazy initialization)
        '''
        # TODO: Specify number of processes
        if not self._thread_pool_executor:
            self._thread_pool_executor = \
                ThreadPoolExecutor(max_workers=self._max_workers)

        return self._thread_pool_executor

    def shutdown(self):
        self._stop_event.set()

        if self._thread_pool:
            self._thread_pool.terminate()
            self._thread_pool.join()

        if self._thread_pool_executor:
            self._thread_pool_executor.shutdown()

        if self._server:
            self._server.close()
            self.loop.run_until_complete(self._server.wait_closed())

        self.loop.stop()

    def start_tcp(self, host, port):
        self._server = self.loop.run_until_complete(
            self.loop.create_server(self.lsp, host, port))
        self.loop.run_forever()

    def start_io(self, stdin=None, stdout=None):
        transport = StdOutTransportAdapter(stdin or sys.stdin.buffer,
                                           stdout or sys.stdout.buffer)
        self.lsp.connection_made(transport)

        self.loop.run_until_complete(aio_readline(self.loop,
                                                  self._thread_pool_executor,
                                                  self._stop_event,
                                                  stdin or sys.stdin.buffer,
                                                  self.lsp.data_received))


class LanguageServer(Server):
    def __init__(self, max_workers=2):
        super().__init__(LanguageServerProtocol, max_workers)

    def command(self, command_name):
        '''
        Registers new command (delegating to FeatureManager).

        Args:
            command_name(str): Name of the command to register
        '''
        return self.lsp.fm.command(command_name)

    def feature(self, *feature_names, **options):
        '''
        Registers one or more LSP features (delegating to FeatureManager).

        Args:
            *feature_names(tuple): One or more features to register
                NOTE: All possible LSP features are listed in lsp module
            **options(dict): Options for registered feature
                E.G. triggerCharacters=['.']
        '''
        return self.lsp.fm.feature(*feature_names, **options)

    def thread(self):
        return self.lsp.thread()
