"""A generic JSON-RPC server"""
import asyncio
import logging
from typing import Dict

from pygls.server import JsonRPCServer

server = JsonRPCServer()


@server.feature("math/add")
def add(params: Dict[str, float]):
    a = params["a"]
    b = params["b"]

    return dict(sum=a + b)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename="server.log", filemode="w")
    asyncio.run(server.start_io())
