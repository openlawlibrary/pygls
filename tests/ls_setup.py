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
import json
import os
import threading

import pytest
from lsprotocol.types import (
    EXIT,
    INITIALIZE,
    SHUTDOWN,
    ClientCapabilities,
    InitializeParams,
)
from pygls.server import LanguageServer


from . import CMD_ASYNC, CMD_SYNC, CMD_THREAD
from ._init_server_stall_fix_hack import retry_stalled_init_fix_hack


CALL_TIMEOUT = 3

def setup_ls_features(server):

    # Commands
    @server.command(CMD_ASYNC)
    async def cmd_test3(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.thread()
    @server.command(CMD_THREAD)
    def cmd_test1(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()

    @server.command(CMD_SYNC)
    def cmd_test2(ls, *args):  # pylint: disable=unused-variable
        return True, threading.get_ident()


class PyodideTestTransportAdapter:
    """Transort adapter that's only useful for tests in a pyodide environment."""

    def __init__(self, dest: LanguageServer):
        self.dest = dest

    def close(self):
        ...

    def write(self, data):
        object_hook = self.dest.lsp._deserialize_message
        self.dest.lsp._procedure_handler(
            json.loads(data, object_hook=object_hook)
        )


class PyodideClientServer:
    """Implementation of the `client_server` fixture for use in a pyodide
    environment."""

    def __init__(self, LS=LanguageServer):

        self.server = LS('pygls-server', 'v1')
        self.client = LS('pygls-client', 'v1')

        self.server.lsp.connection_made(PyodideTestTransportAdapter(self.client))
        self.server.lsp._send_only_body = True

        self.client.lsp.connection_made(PyodideTestTransportAdapter(self.server))
        self.client.lsp._send_only_body = True

    def start(self):
        self.initialize()

    def stop(self):
        ...

    @classmethod
    def decorate(cls):
        return pytest.mark.parametrize(
            'client_server',
            [cls],
            indirect=True
        )

    def initialize(self):
        response = self.client.lsp.send_request(
            INITIALIZE,
            InitializeParams(
                process_id=12345,
                root_uri="file://",
                capabilities=ClientCapabilities()
            )
        ).result(timeout=CALL_TIMEOUT)

        assert response.capabilities is not None

    def __iter__(self):
        yield self.client
        yield self.server


class NativeClientServer:
    def __init__(self, LS=LanguageServer):
        # Client to Server pipe
        csr, csw = os.pipe()
        # Server to client pipe
        scr, scw = os.pipe()

        # Setup Server
        self.server = LS('server', 'v1')
        self.server_thread = threading.Thread(
            name='Server Thread',
            target=self.server.start_io,
            args=(os.fdopen(csr, "rb"), os.fdopen(scw, "wb")),
        )
        self.server_thread.daemon = True

        # Setup client
        self.client = LS('client', 'v1', asyncio.new_event_loop())
        self.client_thread = threading.Thread(
            name='Client Thread',
            target=self.client.start_io,
            args=(os.fdopen(scr, "rb"), os.fdopen(csw, "wb")),
        )
        self.client_thread.daemon = True

    @classmethod
    def decorate(cls):
        return pytest.mark.parametrize(
            'client_server',
            [cls],
            indirect=True
        )

    def start(self):
        self.server_thread.start()
        self.server.thread_id = self.server_thread.ident
        self.client_thread.start()
        self.initialize()

    def stop(self):
        shutdown_response = self.client.lsp.send_request(
            SHUTDOWN
        ).result()
        assert shutdown_response is None
        self.client.lsp.notify(EXIT)
        self.server_thread.join()
        self.client._stop_event.set()
        try:
            self.client.loop._signal_handlers.clear()  # HACK ?
        except AttributeError:
            pass
        self.client_thread.join()

    @retry_stalled_init_fix_hack()
    def initialize(self):

        timeout = None if 'DISABLE_TIMEOUT' in os.environ else 1
        response = self.client.lsp.send_request(
            INITIALIZE,
            InitializeParams(
                process_id=12345,
                root_uri="file://",
                capabilities=ClientCapabilities()
            ),
        ).result(timeout=timeout)
        assert response.capabilities is not None

    def __iter__(self):
        yield self.client
        yield self.server
