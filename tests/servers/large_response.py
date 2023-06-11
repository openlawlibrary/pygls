"""This server returns a particuarly large response."""
import asyncio
import threading
import sys
from concurrent.futures import ThreadPoolExecutor

from pygls.server import aio_readline

def handler(data):
    payload = dict(
        jsonrpc="2.0",
        id=1,
        result=dict(
            numbers=list(range(100_000)),
        ),
    )
    content = str(payload).replace("'", '"')
    print(f'Content-Length: {len(content)}\r\n\r\n{content}', flush=True)


async def main():
    await aio_readline(
        asyncio.get_running_loop(),
        ThreadPoolExecutor(),
        threading.Event(),
        sys.stdin.buffer,
        handler
    )


if __name__ == "__main__":
    asyncio.run(main())
