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
import sys

import pytest
import pytest_asyncio
from lsprotocol import types

from pygls import uris, IS_PYODIDE, IS_WIN
from pygls.feature_manager import FeatureManager
from pygls.workspace import Document, Workspace

from .ls_setup import (
    NativeClientServer,
    PyodideClientServer,
    setup_ls_features,
)

from .client import make_test_lsp_client

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
    if hasattr(request, "param"):
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
def uri_for():
    """Returns the uri corresponsing to a file in the example workspace."""
    base_dir = pathlib.Path(__file__, "..", "..", "examples", "workspace").resolve()

    def fn(*args):
        fpath = pathlib.Path(base_dir, *args)
        return uris.from_fs_path(str(fpath))

    return fn


@pytest.fixture()
def event_loop():
    """Redefine `pytest-asyncio's default event_loop fixture to match the scope
    of our client fixture."""

    # Only required for Python 3.7 on Windows.
    if sys.version_info.minor == 7 and IS_WIN:
        policy = asyncio.WindowsProactorEventLoopPolicy()
    else:
        policy = asyncio.get_event_loop_policy()

    loop = policy.new_event_loop()
    yield loop

    try:
        # Not implemented on pyodide
        loop.close()
    except NotImplementedError:
        pass


@pytest.fixture(scope="session")
def server_dir():
    """Returns the directory where all the example language servers live"""
    path = pathlib.Path(__file__) / ".." / ".." / "examples" / "servers"
    return path.resolve()


@pytest_asyncio.fixture()
async def json_server_client(server_dir, uri_for):
    """Returns a language client connected to server_dir/json_server.py."""

    if IS_PYODIDE:
        pytest.skip("subprocesses are not available in pyodide")

    client = make_test_lsp_client()
    await client.start_io(sys.executable, str(server_dir / "json_server.py"))

    # Initialize the server
    response = await client.initialize_async(
        types.InitializeParams(
            capabilities=types.ClientCapabilities(),
            root_uri=uri_for("."),  # root of example workspace
        )
    )
    assert response is not None

    yield client, response

    await client.shutdown_async(None)
    client.exit(None)

    await client.stop()


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
