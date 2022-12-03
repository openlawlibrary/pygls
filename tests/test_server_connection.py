import asyncio
import json
import os
from threading import Thread
from unittest.mock import Mock

import pytest

from pygls import IS_PYODIDE
from pygls.server import LanguageServer

try:
    import websockets

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


@pytest.mark.asyncio
@pytest.mark.skipif(IS_PYODIDE, reason='threads are not available in pyodide.')
async def test_tcp_connection_lost():
    loop = asyncio.new_event_loop()

    server = LanguageServer('pygls-test', 'v1', loop=loop)

    server.lsp.connection_made = Mock()
    server.lsp.connection_lost = Mock()

    # Run the server over TCP in a separate thread
    server_thread = Thread(
        target=server.start_tcp,
        args=(
            "127.0.0.1",
            0,
        ),
    )
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to be ready
    while server._server is None:
        await asyncio.sleep(0.5)

    # Simulate client's connection
    port = server._server.sockets[0].getsockname()[1]
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    await asyncio.sleep(1)

    assert server.lsp.connection_made.called

    # Socket is closed (client's process is terminated)
    writer.close()
    await asyncio.sleep(1)

    assert server.lsp.connection_lost.called


@pytest.mark.asyncio
@pytest.mark.skipif(IS_PYODIDE, reason='threads are not available in pyodide.')
async def test_io_connection_lost():
    # Client to Server pipe.
    csr, csw = os.pipe()
    # Server to client pipe.
    scr, scw = os.pipe()

    server = LanguageServer('pygls-test', 'v1', loop=asyncio.new_event_loop())
    server.lsp.connection_made = Mock()
    server_thread = Thread(
        target=server.start_io,
        args=(
            os.fdopen(csr, "rb"),
            os.fdopen(scw, "wb")
        )
    )
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to be ready
    while not server.lsp.connection_made.called:
        await asyncio.sleep(0.5)

    # Pipe is closed (client's process is terminated)
    os.close(csw)
    server_thread.join()


@pytest.mark.asyncio
@pytest.mark.skipif(
    IS_PYODIDE or not WEBSOCKETS_AVAILABLE,
    reason="threads are not available in pyodide",
)
async def test_ws_server():
    """Smoke test to ensure we can send/receive messages over websockets"""

    loop = asyncio.new_event_loop()
    server = LanguageServer('pygls-test', 'v1', loop=loop)

    # Run the server over Websockets in a separate thread
    server_thread = Thread(
        target=server.start_ws,
        args=(
            "127.0.0.1",
            0,
        ),
    )
    server_thread.daemon = True
    server_thread.start()

    # Wait for server to be ready
    while server._server is None:
        await asyncio.sleep(0.5)

    port = server._server.sockets[0].getsockname()[1]
    # Simulate client's connection
    async with websockets.connect(f"ws://127.0.0.1:{port}") as connection:

        # Send an 'initialize' request
        msg = dict(
            jsonrpc="2.0", id=1, method="initialize", params=dict(capabilities=dict())
        )
        await connection.send(json.dumps(msg))

        response = await connection.recv()
        assert "result" in response

        # Shut the server down
        msg = dict(
            jsonrpc="2.0", id=2, method="shutdown", params=dict(capabilities=dict())
        )
        await connection.send(json.dumps(msg))

        response = await connection.recv()
        assert "result" in response

        # Finally, tell it to exit
        msg = dict(jsonrpc="2.0", id=2, method="exit", params=None)
        await connection.send(json.dumps(msg))

    server_thread.join()
