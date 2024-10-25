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
from __future__ import annotations

import asyncio
import json
import logging
import re
import typing

from pygls.exceptions import JsonRpcException

if typing.TYPE_CHECKING:
    import logging
    import threading
    from collections.abc import Awaitable
    from concurrent.futures import ThreadPoolExecutor
    from typing import Any, BinaryIO, Callable, Protocol

    from pygls.protocol import JsonRPCProtocol

    class Reader(Protocol):
        """An synchronous reader."""

        def readline(self) -> bytes: ...

        def read(self, n: int) -> bytes: ...

    class AsyncReader(typing.Protocol):
        """An asynchronous reader."""

        def readline(self) -> Awaitable[bytes]: ...

        def readexactly(self, n: int) -> Awaitable[bytes]: ...


class StdinAsyncReader:
    """Read from stdin asynchronously."""

    def __init__(self, stdin: BinaryIO, executor: ThreadPoolExecutor | None = None):
        self.stdin = stdin
        self._loop: asyncio.AbstractEventLoop | None = None
        self.executor = executor

    @property
    def loop(self):
        if self._loop is None:
            self._loop = asyncio.get_running_loop()

        return self._loop

    def readline(self) -> Awaitable[bytes]:
        return self.loop.run_in_executor(self.executor, self.stdin.readline)

    def readexactly(self, n: int) -> Awaitable[bytes]:
        return self.loop.run_in_executor(self.executor, self.stdin.read, n)


async def run_async(
    stop_event: threading.Event,
    reader: AsyncReader,
    protocol: JsonRPCProtocol,
    logger: logging.Logger | None = None,
    error_handler: Callable[[Exception, type[JsonRpcException]], Any] | None = None,
):
    """Run a main message processing loop, asynchronously

    Parameters
    ----------
    stop_event
       A ``threading.Event`` used to break the main loop

    reader
       The reader to read messages from

    protocol
       The protocol instance that should handle the messages

    logger
       The logger instance to use
    """

    CONTENT_LENGTH_PATTERN = re.compile(rb"^Content-Length: (\d+)\r\n$")
    content_length = 0
    logger = logger or logging.getLogger(__name__)

    while not stop_event.is_set():
        # Read a header line
        header = await reader.readline()
        if not header:
            break

        # Extract content length if possible
        if not content_length:
            match = CONTENT_LENGTH_PATTERN.fullmatch(header)
            if match:
                content_length = int(match.group(1))
                logger.debug("Content length: %s", content_length)

        # Check if all headers have been read (as indicated by an empty line \r\n)
        if content_length and not header.strip():
            # Read body
            body = await reader.readexactly(content_length)
            if not body:
                break

            try:
                message = json.loads(body, object_hook=protocol.structure_message)
                protocol.handle_message(message)
            except Exception as exc:
                logger.exception("Unable to handle message")
                if error_handler:
                    error_handler(exc, JsonRpcException)
            finally:
                # Reset
                content_length = 0


def run(
    stop_event: threading.Event,
    reader: Reader,
    protocol: JsonRPCProtocol,
    logger: logging.Logger | None = None,
    error_handler: Callable[[Exception, type[JsonRpcException]], Any] | None = None,
):
    """Run a main message processing loop, synchronously

    Parameters
    ----------
    stop_event
       A ``threading.Event`` used to break the main loop

    reader
       The reader to read messages from

    protocol
       The protocol instance that should handle the messages

    logger
       The logger instance to use

    error_handler
       Function to call when an error is encountered.
    """

    CONTENT_LENGTH_PATTERN = re.compile(rb"^Content-Length: (\d+)\r\n$")
    content_length = 0
    logger = logger or logging.getLogger(__name__)

    while not stop_event.is_set():
        # Read a header line
        header = reader.readline()
        if not header:
            break

        # Extract content length if possible
        if not content_length:
            match = CONTENT_LENGTH_PATTERN.fullmatch(header)
            if match:
                content_length = int(match.group(1))
                logger.debug("Content length: %s", content_length)

        # Check if all headers have been read (as indicated by an empty line \r\n)
        if content_length and not header.strip():
            # Read body
            body = reader.read(content_length)
            if not body:
                break

            try:
                message = json.loads(body, object_hook=protocol.structure_message)
                protocol.handle_message(message)
            except Exception as exc:
                logger.exception("Unable to handle message")
                if error_handler:
                    error_handler(exc, JsonRpcException)
            finally:
                # Reset
                content_length = 0
