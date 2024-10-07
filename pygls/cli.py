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
"""A simple cli wrapper for pygls servers."""
from __future__ import annotations

import argparse
import typing

if typing.TYPE_CHECKING:
    from pygls.server import JsonRPCServer


def start_server(server: JsonRPCServer, args: list[str] | None = None):
    """A helper function that implements a simple cli wrapper for a pygls server
    allowing the user to select between the supported transports."""

    name = type(server).__name__
    parser = argparse.ArgumentParser(description=f"start a {name} instance")
    parser.add_argument("--tcp", action="store_true", help="start a TCP server")
    parser.add_argument("--ws", action="store_true", help="start a WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="bind to this address")
    parser.add_argument("--port", type=int, default=8888, help="bind to this port")

    arguments = parser.parse_args(args)

    if arguments.tcp:
        server.start_tcp(arguments.host, arguments.port)
    elif arguments.ws:
        server.start_ws(arguments.host, arguments.port)
    else:
        server.start_io()
