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
import pathlib

import pytest

from pygls import uris, IS_PYODIDE
from pygls.feature_manager import FeatureManager
from pygls.workspace import Document, Workspace

from .ls_setup import (
    NativeClientServer,
    PyodideClientServer,
    setup_ls_features,
)


DOC = """document
for
testing
with "😋" unicode.
"""
DOC_URI = uris.from_fs_path(__file__)


ClientServer = NativeClientServer
if IS_PYODIDE:
    ClientServer = PyodideClientServer


@pytest.fixture(autouse=False)
def client_server(request):
    if hasattr(request, 'param'):
        ConfiguredClientServer = request.param
        client_server = ConfiguredClientServer()
    else:
        client_server = ClientServer()
        setup_ls_features(client_server.server)

    client_server.start()
    client, server = client_server

    yield client, server

    client_server.stop()


@pytest.fixture(scope="session")
def server_dir():
    """Returns the directory where all the example language servers live"""
    path = pathlib.Path(__file__) / ".." / ".." / "examples" / "servers"
    return path.resolve()


@pytest.fixture(scope="session")
def workspace_dir():
    """Returns the directory containing the example workspace."""
    path = pathlib.Path(__file__) / ".." / ".." / "examples" / "workspace"
    return path.resolve()


@pytest.fixture(scope="session")
def event_loop():
    """Redefine `pytest-asyncio's default event_loop fixture to match the scope
    of our client fixture."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def doc():
    return Document(DOC_URI, DOC)


@pytest.fixture
def feature_manager():
    """Return a feature manager"""
    return FeatureManager()


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(uris.from_fs_path(str(tmpdir)))
