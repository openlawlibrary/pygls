import asyncio
import logging
import traceback
from typing import Any

import websockets

from pygls.protocol import JsonRPCProtocol

logger = logging.getLogger(__name__)


async def ws_reader(ls, websocket, stop_event, proxy):
    """Handle new connection wrapped in the WebSocket."""
    ls.lsp.transport = WebSocketTransportAdapter(websocket, ls.loop)

    while not stop_event.is_set():
        async for message in websocket:
            proxy(message)


class WebSocketTransportAdapter:
    """Protocol adapter which calls write method.
    Write method sends data via the WebSocket interface.
    """

    def __init__(self, ws: websockets.WebSocketServerProtocol, loop):
        self._ws = ws
        self._loop = loop

    def close(self) -> None:
        """Stop the WebSocket server."""
        self._ws.close()

    def write(self, data: Any) -> None:
        """Create a task to write specified data into a WebSocket."""
        asyncio.create_task(self._ws.send(data))


class WebsocketJsonRPCProtocol(JsonRPCProtocol):

    def _send_data(self, data):
        """Sends data to the client over websocket."""
        if not data:
            return

        try:
            body = data.json(by_alias=True, exclude_unset=True)
            logger.info('Sending data: %s', body)

            body = body.encode(self.CHARSET)
            self.transport.write(body.decode('utf-8'))
        except Exception:
            logger.error(traceback.format_exc())
