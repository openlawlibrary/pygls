##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
import logging
import socketserver
import sys

from .endpoint import Endpoint
from .streams import JsonRpcStreamReader, JsonRpcStreamWriter

log = logging.getLogger(__name__)


class _StreamHandlerWrapper(socketserver.StreamRequestHandler, object):
    """A wrapper class that is used to construct a custom handler class."""

    delegate = None

    def handle(self):
        self.delegate.start()

    def setup(self):
        super().setup()
        self.delegate.setup_streams(self.rfile, self.wfile)


class JsonRPCServer(object):

    def setup_streams(self, rx, tx):
        self._jsonrpc_stream_reader = JsonRpcStreamReader(rx)
        self._jsonrpc_stream_writer = JsonRpcStreamWriter(tx)
        self._endpoint = Endpoint(self, self._jsonrpc_stream_writer.write)

    def start(self):
        """Entry point for the server."""
        self._jsonrpc_stream_reader.listen(self._endpoint.consume)

    def start_io(self, stdin=None, stdout=None):
        log.info(f'Starting {JsonRPCServer.__name__} IO language server')
        self.setup_streams(stdin or sys.stdin.buffer,
                           stdout or sys.stdout.buffer)
        self.start()

    def start_tcp(self, bind_addr, port):
        # Construct a custom wrapper class around the user's handler_class
        wrapper_class = type(
            JsonRPCServer.__name__ + 'Handler',
            (_StreamHandlerWrapper,),
            {'delegate': self}
        )

        server = socketserver.TCPServer((bind_addr, port), wrapper_class)
        try:
            log.info(
                'Serving {JsonRPCServer.__name__} on ({bind_addr}, {port})')
            server.serve_forever()
        finally:
            log.info('Shutting down')
            server.server_close()
