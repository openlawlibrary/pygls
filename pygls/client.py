############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
import asyncio
import logging
import re
from threading import Event
from typing import Callable
from typing import List
from typing import Optional
from typing import Type

from cattrs import Converter

from pygls.protocol import JsonRPCProtocol, default_converter


logger = logging.getLogger(__name__)


async def aio_readline(stop_event, reader, message_handler):

    CONTENT_LENGTH_PATTERN = re.compile(rb'^Content-Length: (\d+)\r\n$')

    # Initialize message buffer
    message = []
    content_length = 0

    while not stop_event.is_set():
        # Read a header line
        header = await reader.readline()
        if not header:
            break
        message.append(header)

        # Extract content length if possible
        if not content_length:
            match = CONTENT_LENGTH_PATTERN.fullmatch(header)
            if match:
                content_length = int(match.group(1))
                logger.debug('Content length: %s', content_length)

        # Check if all headers have been read (as indicated by an empty line \r\n)
        if content_length and not header.strip():

            # Read body
            body = await reader.read(content_length)
            if not body:
                break
            message.append(body)

            # Pass message to protocol
            message_handler(b''.join(message))

            # Reset the buffer
            message = []
            content_length = 0


class Client:
    """Base JSON-RPC client."""

    def __init__(
        self,
        protocol_cls: Type[JsonRPCProtocol] = JsonRPCProtocol,
        converter_factory: Callable[[], Converter] = default_converter,
    ):

        self.protocol = protocol_cls(self, converter_factory())

        self._server: Optional[asyncio.subprocess.Process] = None
        self._stop_event = Event()
        self._async_tasks: List[asyncio.Task] = []

    async def start_io(self, cmd: str, *args, **kwargs):
        """Start the given server and communicate with it over stdio."""

        server = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            **kwargs,
        )

        self.protocol.connection_made(server.stdin)  # type: ignore
        connection = asyncio.create_task(
            aio_readline(
                self._stop_event,
                server.stdout,
                self.protocol.data_received
            )
        )
        self._server = server
        self._async_tasks.append(connection)

    async def stop(self):
        self._stop_event.set()

        if len(self._async_tasks) > 0:
            await asyncio.gather(*self._async_tasks)
