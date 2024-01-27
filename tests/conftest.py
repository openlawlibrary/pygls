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

from pygls import uris
from pygls.lsp.client import LanguageClient as LanguageClient_
from pygls.workspace import Workspace

DOC = """document
for
testing
with "😋" unicode.
"""
DOC_URI = uris.from_fs_path(__file__) or ""
REPO_DIR = pathlib.Path(__file__, "..", "..").resolve()
SERVER_DIR = REPO_DIR / "examples" / "servers"
WORKSPACE_DIR = REPO_DIR / "examples" / "servers" / "workspace"
WASI_DIR = REPO_DIR / "tests" / "wasi"

REPO_DIR = pathlib.Path(__file__, "..", "..").resolve()
SERVER_DIR = REPO_DIR / "examples" / "servers"
WORKSPACE_DIR = REPO_DIR / "examples" / "servers" / "workspace"


@pytest.fixture(scope="session")
def event_loop():
    """Redefine `pytest-asyncio's default event_loop fixture to match the scope
    of our client fixture."""
    # TODO: Remove for pytest-asyncio 0.23.x
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop

    try:
        # Not implemented for pyodide's event loop
        loop.close()
    except NotImplementedError:
        pass


@pytest.fixture
def workspace(tmpdir):
    """Return a workspace."""
    return Workspace(
        uris.from_fs_path(str(tmpdir)),
        sync_kind=types.TextDocumentSyncKind.Incremental,
    )


class LanguageClient(LanguageClient_):
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
        choices=("cpython", "pyodide", "wasi"),
        help="Choose the runtime in which to run servers under test.",
    )


@pytest.fixture(scope="session")
def runtime(request):
    """This fixture is the source of truth as to which environment we should run the
    end-to-end tests in."""
    return request.config.getoption("lsp_runtime")


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

        if runtime == "pyodide":
            # Pyodide cannot see the whole file system, so this needs to be made relative to
            # the workspace's parent folder
            path = str(fpath).replace(str(WORKSPACE_DIR.parent), "")
            uri = uris.from_fs_path(path)

        elif runtime == "wasi":
            # WASI cannot see the whole filesystem, so this needs to be made relative to
            # the repo root
            path = str(fpath).replace(str(REPO_DIR), "")
            uri = uris.from_fs_path(path)

        else:
            uri = uris.from_fs_path(str(fpath))

        assert uri is not None
        return uri

    return fn


@pytest.fixture(scope="session")
def server_dir():
    """Returns the directory where all the example language servers live"""
    path = pathlib.Path(__file__) / ".." / ".." / "examples" / "servers"
    return path.resolve()


def get_client_for_cpython_server(uri_fixture):
    """Return a client configured to communicate with a server running under cpython."""

    async def fn(server_name: str):
        client = LanguageClient("pygls-test-suite", "v1")
        await client.start_io(sys.executable, str(SERVER_DIR / server_name))

        response = await client.initialize(
            types.InitializeParams(
                capabilities=types.ClientCapabilities(),
                root_uri=uri_fixture(""),
            )
        )
        assert response is not None
        yield client, response

        await client.shutdown(None)
        client.exit(None)

        await client.stop()

    return fn


def get_client_for_pyodide_server(uri_fixture):
    """Return a client configured to communicate with a server running under Pyodide.

    This assumes that the pyodide environment has already been bootstrapped.
    """

    async def fn(server_name: str):
        client = LanguageClient("pygls-test-suite", "v1")

        PYODIDE_DIR = REPO_DIR / "tests" / "pyodide"
        server_py = str(SERVER_DIR / server_name)

        await client.start_io("node", str(PYODIDE_DIR / "run_server.js"), server_py)

        response = await client.initialize(
            types.InitializeParams(
                capabilities=types.ClientCapabilities(),
                root_uri=uri_fixture(""),
            )
        )
        assert response is not None
        yield client, response

        await client.shutdown(None)
        client.exit(None)

        await client.stop()

    return fn


def get_client_for_wasi_server(uri_fixture):
    """Return a client configured to communicate with a server running under WASI.

    This assumes the ``wasmtime`` executable is available to be used as the WASI host.
    """

    async def fn(server_name: str):
        client = LanguageClient("pygls-test-suite", "v1")

        # WASI cannot see the whole filesystem, so this needs to be made relative to the
        # repo root
        server_py = str(SERVER_DIR / server_name).replace(str(REPO_DIR), "")

        # fmt: off
        await client.start_io(
            "wasmtime", "run",
            # Tell python where its standard library lives and grant access to it.
            "--env", f"PYTHONHOME={WASI_DIR}",
            "--dir", str(WASI_DIR),
            # Grant access to the current working directory
            "--dir", ".",
            str(WASI_DIR / "python.wasm"),
            # Everything from here will be passed to Python itself
            server_py,
        )
        # fmt: on

        response = await client.initialize(
            types.InitializeParams(
                capabilities=types.ClientCapabilities(),
                root_uri=uri_fixture(""),
            )
        )
        assert response is not None
        yield client, response

        await client.shutdown(None)
        client.exit(None)

        await client.stop()

    return fn


@pytest.fixture(scope="session")
def get_client_for(runtime, uri_for):
    """Return a client configured to communicate with the specified server.

    Takes into account the current runtime.

    It's the consuming fixture's responsibility to stop the client.
    """
    # TODO: Add TCP/WS support.
    if runtime not in {"cpython", "pyodide", "wasi"}:
        raise NotImplementedError(f"get_client_for: {runtime=}")

    elif runtime == "pyodide":
        return get_client_for_pyodide_server(uri_for)

    elif runtime == "wasi":
        return get_client_for_wasi_server(uri_for)

    return get_client_for_cpython_server(uri_for)
