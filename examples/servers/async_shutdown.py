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

from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer

server = LanguageServer("async-shutdown-server", "v1")


@server.feature(types.SHUTDOWN)
async def shutdown(params: None) -> None:
    """An async shutdown handler that is long and complicated and takes a while to
    complete"""

    logging.info("Shutdown started")
    server.window_log_message(
        types.LogMessageParams(message="Shutdown started", type=types.MessageType.Info)
    )

    await asyncio.sleep(10)

    server.window_log_message(
        types.LogMessageParams(message="Shutdown complete", type=types.MessageType.Info)
    )
    logging.info("Shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
