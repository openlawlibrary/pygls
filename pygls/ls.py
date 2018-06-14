'''
This module contains LanguageServer
There are two ways of starting it:
 - start_tcp
 - start_io
'''

# Copyright 2017 Palantir Technologies, Inc.
import logging
import socketserver
import sys
import functools
import inspect

from .lsp_impl import LSPBase
from .jsonrpc.endpoint import Endpoint
from .jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter

log = logging.getLogger(__name__)


class _StreamHandlerWrapper(socketserver.StreamRequestHandler, object):
    """A wrapper class that is used to construct a custom handler class."""

    delegate = None

    def setup(self):
        super(_StreamHandlerWrapper, self).setup()
        self.delegate.setup_streams(self.rfile, self.wfile)

    def handle(self):
        self.delegate.start()


class LanguageServer(LSPBase):
    """ Implementation of the Microsoft VSCode Language Server Protocol
    https://github.com/Microsoft/language-server-protocol/blob/master/versions/protocol-1-x.md
    """

    def __init__(self):
        super(LanguageServer, self).__init__()

    def __getitem__(self, item):
        try:
            try:
                # Look at base features
                method = self._base_features[item]
            except:
                # Look at user defined features
                method = self._features[item]

            @functools.wraps(method)
            def handler(params):
                args = inspect.getargspec(method)[0]
                if 'ls' in args:
                    return method(ls=self, **(params or {}))
                else:
                    return method(**(params or {}))

            return handler
        except:
            # log
            raise KeyError()

    def setup_streams(self, rx, tx):
        self._jsonrpc_stream_reader = JsonRpcStreamReader(rx)
        self._jsonrpc_stream_writer = JsonRpcStreamWriter(tx)
        self._endpoint = Endpoint(self, self._jsonrpc_stream_writer.write)

    def start_tcp(self, bind_addr, port):
        # Construct a custom wrapper class around the user's handler_class
        wrapper_class = type(
            LanguageServer.__name__ + 'Handler',
            (_StreamHandlerWrapper,),
            {'delegate': self}
        )

        server = socketserver.TCPServer((bind_addr, port), wrapper_class)
        try:
            log.info('Serving %s on (%s, %s)',
                     LanguageServer.__name__, bind_addr, port)
            server.serve_forever()
        finally:
            log.info('Shutting down')
            server.server_close()

    def start_io(self):
        log.info('Starting %s IO language server', handler_class.__name__)
        self.setup_streams(sys.stdin.buffer, sys.stdout.buffer)
        self.start()

    def start(self):
        """Entry point for the server."""
        self._jsonrpc_stream_reader.listen(self._endpoint.consume)
