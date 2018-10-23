import asyncio
import logging
import os
import sys
from re import findall

from . import IS_WIN
from .protocol import LanguageServerProtocol

logger = logging.getLogger(__name__)


async def aio_readline(loop, rfile, proxy):
    '''
    Read data from stdin in separate thread (asynchronously)
    '''
    while True:
        # Read line
        line = await loop.run_in_executor(None, rfile.readline)

        if not line:
            continue

        # Extract content length from line
        try:
            content_length = int(findall(r'\b\d+\b', line)[0])
            logger.info(content_length)
        except:
            continue

        # Throw away empty lines
        while line and line.strip():
            line = await loop.run_in_executor(None, rfile.readline)

        if not line:
            continue

        # Read body
        body = await loop.run_in_executor(None, rfile.read, content_length)

        # Pass body to language server protocol
        if body:
            proxy(body.encode('utf-8'))


class StdOutTransportAdapter(asyncio.Transport):
    '''
    Protocol adapter which overrides write method.
    Write method sends data to stdout.
    '''

    def __init__(self, wfile):
        self.wfile = wfile

    def close(self):
        self.wfile.close()

    def write(self, data):
        self.wfile.write(data)
        self.wfile.flush()


class Server:
    def __init__(self, protocol_cls):
        assert issubclass(protocol_cls, asyncio.Protocol)

        if IS_WIN:
            asyncio.set_event_loop(asyncio.ProactorEventLoop())

        self.loop = asyncio.get_event_loop()

        self.lsp = protocol_cls(self)
        self.server = None

    def shutdown(self):
        # self.server.close()
        # TODO: Gracefully shutdown event loops
        pass

    def start_tcp(self, host, port):
        self.server = self.loop.run_until_complete(
            self.loop.create_server(self.lsp, host, port)
        )
        self.loop.run_forever()

    def start_io(self, stdin=None, stdout=None):
        transport = StdOutTransportAdapter(stdout or sys.stdout.buffer)
        self.lsp.connection_made(transport)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(aio_readline(loop, stdin or sys.stdin,
                                             self.lsp.data_received))


class LanguageServer(Server):
    def __init__(self):
        super().__init__(LanguageServerProtocol)

    def command(self, command_name):
        '''
        Registers new command (delegating to FeatureManager).

        Args:
            command_name(str): Name of the command to register
        '''
        return self.lsp.fm.command(self, command_name)

    def feature(self, *feature_names, **options):
        '''
        Registers one or more LSP features (delegating to FeatureManager).

        Args:
            *feature_names(tuple): One or more features to register
                NOTE: All possible LSP features are listed in lsp module
            **options(dict): Options for registered feature
                E.G. triggerCharacters=['.']
        '''
        return self.lsp.fm.feature(self, *feature_names, **options)

    def thread(self):
        return self.lsp.thread()
