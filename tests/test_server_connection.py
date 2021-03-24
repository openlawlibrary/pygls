import asyncio
from threading import Thread
from unittest.mock import Mock

import pytest

from pygls.server import LanguageServer


@pytest.mark.asyncio
async def test_tcp_connection_lost():
    loop = asyncio.new_event_loop()

    server = LanguageServer(loop=loop)

    server.lsp.connection_made = Mock()
    server.lsp.connection_lost = Mock()

    # Run the server over TCP in a separate thread
    server_thread = Thread(target=server.start_tcp, args=(
        'localhost', 8080
    ))
    server_thread.daemon = True
    server_thread.start()

    # Simulate client's connection
    reader, writer = await asyncio.open_connection('localhost', 8080)
    await asyncio.sleep(1)

    assert server.lsp.connection_made.called

    # Socket is closed (client's process is terminated)
    writer.close()
    await asyncio.sleep(1)

    assert server.lsp.connection_lost.called
