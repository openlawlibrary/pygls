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
import sys
from typing import BinaryIO
from typing import Optional
from typing import Tuple
from typing import Type

from pygls.protocol import JsonRPCHandler
from pygls.protocol import JsonRPCProtocol
from pygls.protocol import rpc_main_loop


class JsonRPCServer(JsonRPCHandler):
    """Base JSON-RPC server compatible with asyncio."""

    def __init__(
        self, *args, protocol_cls: Type[JsonRPCProtocol] = JsonRPCProtocol, **kwargs
    ):
        super().__init__(*args, protocol=protocol_cls(), **kwargs)

    async def start_io(
        self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None
    ):
        stdin = stdin or sys.stdin.buffer
        stdout = stdout or sys.stdout.buffer

        reader, writer = await get_sdtio_streams(stdin, stdout)
        self._writer = writer

        await rpc_main_loop(
            reader=reader,
            stop_event=self._stop_event,
            message_handler=self,
        )


async def get_sdtio_streams(
    stdin: BinaryIO, stdout: BinaryIO
) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    """Get async stdio streams to use with the server."""

    # TODO: This only works on linux!
    loop = asyncio.get_running_loop()

    reader = asyncio.StreamReader()
    read_protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: read_protocol, stdin)

    write_transport, write_protocol = await loop.connect_write_pipe(
        asyncio.streams.FlowControlMixin, stdout
    )
    writer = asyncio.StreamWriter(write_transport, write_protocol, reader, loop)
    return reader, writer
