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
import sys
from typing import BinaryIO
from typing import Optional
from typing import Type

from pygls.protocol import JsonRPCHandler
from pygls.protocol import JsonRPCProtocol
from pygls.protocol import rpc_main_loop


class JsonRPCServer(JsonRPCHandler):
    """Base JSON-RPC server built on the syncronous JsonRPCHandler."""

    def __init__(
        self, *args, protocol_cls: Type[JsonRPCProtocol] = JsonRPCProtocol, **kwargs
    ):
        super().__init__(*args, protocol=protocol_cls(), **kwargs)

    def start_io(
        self, stdin: Optional[BinaryIO] = None, stdout: Optional[BinaryIO] = None
    ):
        self._writer = stdout or sys.stdout.buffer

        rpc_main_loop(
            reader=stdin or sys.stdin.buffer,
            stop_event=self._stop_event,
            message_handler=self,
        )
