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
import logging

from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer

server = LanguageServer("register-during-init-server", "v1")


@server.feature(types.INITIALIZE)
def initialize(params: types.InitializeParams):
    """An initialize handler that only registers a ``textDocument/formatting`` handler
    if the user requests it in their initialzation options."""

    init_options = params.initialization_options or {}
    if init_options.get("formatting", False):

        @server.feature(types.TEXT_DOCUMENT_FORMATTING)
        async def format_document(
            ls: LanguageServer, params: types.DocumentFormattingParams
        ):
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
