############################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.                 #
# Original work licensed under the MIT License.                            #
# See ThirdPartyNotices.txt in the project root for license information.   #
# All modifications Copyright (c) Open Law Library. All rights reserved.   #
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
import os
from threading import Thread
from time import sleep
from typing import List

import pygls.lsp.methods
import pytest
from pygls import uris
from pygls.feature_manager import FeatureManager
from pygls.lsp.methods import INITIALIZE
from pygls.lsp.types import ClientCapabilities, InitializeParams
from pygls.server import LanguageServer
from pygls.workspace import Document, Workspace

from tests.ls_setup import setup_ls_features

CALL_TIMEOUT = 3

DOC = """document
for
testing
with "😋" unicode.
"""
DOC_URI = uris.from_fs_path(__file__)


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    sleep(CALL_TIMEOUT)
    for cs in ClientServer._to_stop:
       cs._stop()


class ClientServer:
    _to_stop: List['ClientServer'] = []

    def __init__(self):
        # Client to Server pipe
        csr, csw = os.pipe()
        # Server to client pipe
        scr, scw = os.pipe()

        # Setup Server
        self.server = LanguageServer()
        self.server_thread = Thread(target=self.server.start_io, args=(
            os.fdopen(csr, 'rb'), os.fdopen(scw, 'wb')
        ))
        self.server_thread.daemon = True

        # Setup client
        self.client = LanguageServer(asyncio.new_event_loop())
        self.client_thread = Thread(target=self.client.start_io, args=(
            os.fdopen(scr, 'rb'), os.fdopen(csw, 'wb')))
        self.client_thread.daemon = True

    def start(self):
        self.server_thread.start()
        self.server.thread_id = self.server_thread.ident

        self.client_thread.start()

        self.initialize()

    def stop(self):
        ClientServer._to_stop.append(self)

    def _stop(self):
        shutdown_response = (
            self.client
            .lsp.send_request(pygls.lsp.methods.SHUTDOWN)
            .result(timeout=CALL_TIMEOUT)
        )
        assert shutdown_response is None
        # Exit the server
        self.client.lsp.notify(pygls.lsp.methods.EXIT)
        self.server_thread.join()
        # Exit the client
        self.client._stop_event.set()
        try:
            self.client.loop._signal_handlers.clear() # HACK ?
        except AttributeError:
            pass
        self.client_thread.join()

    def initialize(self):
        response = self.client.lsp.send_request(
            INITIALIZE,
            InitializeParams(
                process_id=12345,
                root_uri="file://",
                capabilities=ClientCapabilities()
            )
        ).result(timeout=CALL_TIMEOUT)

        assert 'capabilities' in response

    def __iter__(self):
        yield self.client
        yield self.server


@pytest.fixture(scope='session', autouse=True)
def client_server():
    """ A fixture to setup a client/server """
    client_server = ClientServer()
    setup_ls_features(client_server.server)

    client_server.start()

    client, server = client_server

    yield client, server

    client_server.stop()


@pytest.fixture
def doc():
    return Document(DOC_URI, DOC)


@pytest.fixture
def feature_manager():
    """ Return a feature manager """
    return FeatureManager()


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(uris.from_fs_path(str(tmpdir)))
