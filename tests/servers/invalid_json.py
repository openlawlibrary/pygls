"""This server does nothing but print invalid JSON."""

import asyncio
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

from pygls.server import aio_readline


def handler(data):
    content = 'Content-Length: 5\r\n\r\n{"ll}'.encode("utf8")
    sys.stdout.buffer.write(content)
    sys.stdout.flush()


async def main():
    await aio_readline(
        asyncio.get_running_loop(),
        ThreadPoolExecutor(),
        threading.Event(),
        sys.stdin.buffer,
        handler,
    )


if __name__ == "__main__":
    asyncio.run(main())
