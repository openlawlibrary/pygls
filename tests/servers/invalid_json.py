"""This server does nothing but print invalid JSON."""
import asyncio
import sys
import threading
from functools import partial

from pygls.protocol import rpc_main_loop
from pygls.server._async_server import get_sdtio_streams


def write_data(writer: asyncio.StreamWriter, data):
    content = 'Content-Length: 5\r\n\r\n{"ll}'.encode("utf8")
    writer.write(content)


async def main():
    reader, writer = await get_sdtio_streams(sys.stdin.buffer, sys.stdout.buffer)

    await rpc_main_loop(
        reader=reader,
        stop_event=threading.Event(),
        message_handler=partial(write_data, writer),
    )


if __name__ == "__main__":
    asyncio.run(main())
