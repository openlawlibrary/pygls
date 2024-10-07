"""This server returns a particuarly large response."""

import sys

from pygls.server import JsonRPCServer
from pygls.protocol import JsonRPCProtocol, default_converter

server = JsonRPCServer(JsonRPCProtocol, default_converter)


@server.feature("get/numbers")
def get_numbers(*args):
    return dict(numbers=list(range(100_000)))


@server.feature("exit")
def exit(*args):
    sys.exit(0)


if __name__ == "__main__":
    server.start_io()
