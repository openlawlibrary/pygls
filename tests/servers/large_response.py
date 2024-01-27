"""This server returns a particuarly large response."""
import asyncio
import sys
import threading
from functools import partial

from pygls.protocol import rpc_main_loop
from pygls.server._async_server import get_sdtio_streams


def write_data(writer, data):
    payload = dict(
        jsonrpc="2.0",
        id=1,
        result=dict(
            numbers=list(range(100_000)),
        ),
    )
    content = str(payload).replace("'", '"')
    message = f"Content-Length: {len(content)}\r\n\r\n{content}".encode("utf8")

    writer.write(message)


async def main():
    reader, writer = await get_sdtio_streams(sys.stdin.buffer, sys.stdout.buffer)

    await rpc_main_loop(
        reader=reader,
        stop_event=threading.Event(),
        message_handler=partial(write_data, writer),
    )


if __name__ == "__main__":
    asyncio.run(main())
