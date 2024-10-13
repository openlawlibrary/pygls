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
from __future__ import annotations

import asyncio
import pathlib
import sys
from typing import Optional

import pytest
from lsprotocol import types, converters

from pygls import uris, IS_PYODIDE
from pygls.feature_manager import FeatureManager
from pygls.lsp.client import BaseLanguageClient
from pygls.workspace import Workspace

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
DOC_URI = uris.from_fs_path(__file__) or ""

REPO_DIR = pathlib.Path(__file__, "..", "..").resolve()
SERVER_DIR = REPO_DIR / "examples" / "servers"
WORKSPACE_DIR = REPO_DIR / "examples" / "servers" / "workspace"


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


@pytest.fixture()
def event_loop():
    """Redefine `pytest-asyncio's default event_loop fixture to match the scope
    of our client fixture."""

    policy = asyncio.get_event_loop_policy()

    loop = policy.new_event_loop()
    yield loop

    try:
        # Not implemented on pyodide
        loop.close()
    except NotImplementedError:
        pass


@pytest.fixture
def feature_manager():
    """Return a feature manager"""
    return FeatureManager(None, converters.get_converter())


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(
        uris.from_fs_path(str(tmpdir)),
        sync_kind=types.TextDocumentSyncKind.Incremental,
    )


class LanguageClient(BaseLanguageClient):
    """Language client to use for testing."""

    async def server_exit(self, server: asyncio.subprocess.Process):
        # -15: terminated (probably by the client)
        #   0: all ok
        if server.returncode not in {-15, 0}:
            if server.stderr is not None:
                err = await server.stderr.read()
                print(f"stderr: {err.decode('utf8')}", file=sys.stderr)


def pytest_addoption(parser):
    """Add extra cli arguments to pytest."""
    group = parser.getgroup("pygls")
    group.addoption(
        "--lsp-runtime",
        dest="lsp_runtime",
        action="store",
        default="cpython",
        choices=("cpython",),
        help="Choose the runtime in which to run servers under test.",
    )

    group.addoption(
        "--lsp-transport",
        dest="lsp_transport",
        action="store",
        default="stdio",
        choices=("stdio", "tcp", "websockets"),
        help="Choose the transport to use with servers under test.",
    )


@pytest.fixture(scope="session")
def runtime(request):
    """This fixture is the source of truth as to which environment we should run the
    end-to-end tests in."""
    return request.config.getoption("lsp_runtime")


@pytest.fixture(scope="session")
def transport(request):
    """This fixture is the source of truth for the transport we should run the
    end-to-end tests with."""
    return request.config.getoption("lsp_transport")


@pytest.fixture(scope="session")
def path_for():
    """Returns the path corresponding to a file in the example workspace"""

    def fn(*args):
        fpath = pathlib.Path(WORKSPACE_DIR, *args)
        assert fpath.exists()

        return fpath

    return fn


@pytest.fixture(scope="session")
def uri_for(runtime, path_for):
    """Returns the uri corresponsing to a file in the example workspace.

    Takes into account the runtime.
    """

    def fn(*args):
        fpath = path_for(*args)
        uri = uris.from_fs_path(str(fpath))

        assert uri is not None
        return uri

    return fn


@pytest.fixture(scope="session")
def server_dir():
    """Returns the directory where all the example language servers live"""
    path = pathlib.Path(__file__) / ".." / ".." / "examples" / "servers"
    return path.resolve()


def get_client_for_cpython_server(transport, uri_fixture):
    """Return a client configured to communicate with a server running under cpython."""

    async def fn(
        server_name: str, capabilities: Optional[types.ClientCapabilities] = None
    ):
        client = LanguageClient("pygls-test-suite", "v1")

        server_cmd = [sys.executable, str(SERVER_DIR / server_name)]
        server: asyncio.subprocess.Process | None = None

        if transport == "stdio":
            await client.start_io(*server_cmd)

        elif transport == "tcp":
            # TODO: Make host/port configurable?
            host, port = "localhost", 8888
            server_cmd.extend(["--tcp", "--host", host, "--port", f"{port}"])

            server = await asyncio.create_subprocess_exec(*server_cmd)
            await asyncio.sleep(1)
            await client.start_tcp(host, port)

        elif transport == "websockets":
            # TODO: Make host/port configurable?
            host, port = "localhost", 8888
            server_cmd.extend(["--ws", "--host", host, "--port", f"{port}"])

            server = await asyncio.create_subprocess_exec(*server_cmd)
            await asyncio.sleep(1)
            await client.start_ws(host, port)

        else:
            raise NotImplementedError(f"Unsupported transport: {transport!r}")

        response = await client.initialize_async(
            types.InitializeParams(
                capabilities=capabilities or types.ClientCapabilities(),
                root_uri=uri_fixture(""),
            )
        )
        assert response is not None
        yield client, response

        await client.shutdown_async(None)
        client.exit(None)

        await client.stop()
        if server is not None and server.returncode is None:
            server.terminate()

    return fn


@pytest.fixture(scope="session")
def get_client_for(runtime, transport, uri_for):
    """Return a client configured to communicate with the specified server.

    Takes into account the current runtime and transport.
    """
    if runtime not in {"cpython"}:
        raise NotImplementedError(f"get_client_for: {runtime=}")

    return get_client_for_cpython_server(transport, uri_for)
