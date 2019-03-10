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

import pytest
from pygls import features, uris
from pygls.feature_manager import FeatureManager
from pygls.server import LanguageServer
from pygls.workspace import Document, Workspace
from tests.ls_setup import setup_ls_features

CALL_TIMEOUT = 2

DOC = """document
for
testing
"""
DOC_URI = uris.from_fs_path(__file__)


@pytest.fixture(scope='session', autouse=True)
def client_server():
    """ A fixture to setup a client/server """

    # Client to Server pipe
    csr, csw = os.pipe()
    # Server to client pipe
    scr, scw = os.pipe()

    # Setup server
    server = LanguageServer()
    setup_ls_features(server)

    server_thread = Thread(target=server.start_io, args=(
        os.fdopen(csr, 'rb'), os.fdopen(scw, 'wb')
    ))

    server_thread.daemon = True
    server_thread.start()

    # Add thread id to the server (just for testing)
    server.thread_id = server_thread.ident

    # Setup client
    client = LanguageServer(asyncio.new_event_loop())

    client_thread = Thread(target=client.start_io, args=(
        os.fdopen(scr, 'rb'), os.fdopen(csw, 'wb')))

    client_thread.daemon = True
    client_thread.start()

    yield client, server

    shutdown_response = client.lsp.send_request(
        features.SHUTDOWN).result(timeout=CALL_TIMEOUT)
    assert shutdown_response is None
    client.lsp.notify(features.EXIT)


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
