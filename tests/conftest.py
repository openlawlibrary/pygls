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
from lsprotocol import types

from pygls import uris, IS_PYODIDE, IS_WIN
from pygls.feature_manager import FeatureManager
from pygls.workspace import Workspace

from .ls_setup import (
    NativeClientServer,
    PyodideClientServer,
    setup_ls_features,
)

from .client import create_client_for_server

DOC = """document
for
testing
with "😋" unicode.
"""
DOC_URI = uris.from_fs_path(__file__) or ""


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


code_action_client = create_client_for_server("code_actions.py")
inlay_hints_client = create_client_for_server("inlay_hints.py")
json_server_client = create_client_for_server("json_server.py")


@pytest.fixture
def feature_manager():
    """Return a feature manager"""
    return FeatureManager()


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(
        uris.from_fs_path(str(tmpdir)),
        sync_kind=types.TextDocumentSyncKind.Incremental,
    )
