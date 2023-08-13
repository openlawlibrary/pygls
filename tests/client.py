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
import logging
import pathlib
import sys
from concurrent.futures import Future
from typing import Dict
from typing import List
from typing import Type

import pytest
import pytest_asyncio
from lsprotocol import types

from pygls import IS_PYODIDE
from pygls import uris
from pygls.exceptions import JsonRpcMethodNotFound
from pygls.lsp.client import BaseLanguageClient
from pygls.protocol import LanguageServerProtocol
from pygls.protocol import default_converter

logger = logging.getLogger(__name__)


class LanguageClientProtocol(LanguageServerProtocol):
    """An extended protocol class with extra methods that are useful for testing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._notification_futures = {}

    def _handle_notification(self, method_name, params):
        if method_name == types.CANCEL_REQUEST:
            self._handle_cancel_notification(params.id)
            return

        future = self._notification_futures.pop(method_name, None)
        if future:
            future.set_result(params)

        try:
            handler = self._get_handler(method_name)
            self._execute_notification(handler, params)
        except (KeyError, JsonRpcMethodNotFound):
            logger.warning("Ignoring notification for unknown method '%s'", method_name)
        except Exception:
            logger.exception(
                "Failed to handle notification '%s': %s", method_name, params
            )

    def wait_for_notification(self, method: str, callback=None):
        future: Future = Future()
        if callback:

            def wrapper(future: Future):
                result = future.result()
                callback(result)

            future.add_done_callback(wrapper)

        self._notification_futures[method] = future
        return future

    def wait_for_notification_async(self, method: str):
        future = self.wait_for_notification(method)
        return asyncio.wrap_future(future)


class LanguageClient(BaseLanguageClient):
    """Language client used to drive test cases."""

    def __init__(
        self,
        protocol_cls: Type[LanguageClientProtocol] = LanguageClientProtocol,
        *args,
        **kwargs,
    ):
        super().__init__(
            "pygls-test-client", "v1", protocol_cls=protocol_cls, *args, **kwargs
        )

        self.diagnostics: Dict[str, List[types.Diagnostic]] = {}
        """Used to hold any recieved diagnostics."""

        self.messages: List[types.ShowMessageParams] = []
        """Holds any received ``window/showMessage`` requests."""

        self.log_messages: List[types.LogMessageParams] = []
        """Holds any received ``window/logMessage`` requests."""

    async def wait_for_notification(self, method: str):
        """Block until a notification with the given method is received.

        Parameters
        ----------
        method
           The notification method to wait for, e.g. ``textDocument/publishDiagnostics``
        """
        return await self.protocol.wait_for_notification_async(method)


def make_test_lsp_client() -> LanguageClient:
    """Construct a new test client instance with the handlers needed to capture
    additional responses from the server."""

    client = LanguageClient(converter_factory=default_converter)

    @client.feature(types.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
    def publish_diagnostics(
        client: LanguageClient, params: types.PublishDiagnosticsParams
    ):
        client.diagnostics[params.uri] = params.diagnostics

    @client.feature(types.WINDOW_LOG_MESSAGE)
    def log_message(client: LanguageClient, params: types.LogMessageParams):
        client.log_messages.append(params)

        levels = ["ERROR: ", "WARNING: ", "INFO: ", "LOG: "]
        log_level = levels[params.type.value - 1]

        print(log_level, params.message)

    @client.feature(types.WINDOW_SHOW_MESSAGE)
    def show_message(client: LanguageClient, params):
        client.messages.append(params)

    return client


def create_client_for_server(server_name: str):
    """Automate the process of creating a language client connected to the given server
    and tearing it down again.
    """

    @pytest_asyncio.fixture
    async def fixture_func():
        if IS_PYODIDE:
            pytest.skip("not available in pyodide")

        client = make_test_lsp_client()
        server_dir = pathlib.Path(__file__, "..", "..", "examples", "servers").resolve()
        root_dir = pathlib.Path(__file__, "..", "..", "examples", "workspace").resolve()

        await client.start_io(sys.executable, str(server_dir / server_name))

        # Initialize the server
        response = await client.initialize_async(
            types.InitializeParams(
                capabilities=types.ClientCapabilities(),
                root_uri=uris.from_fs_path(root_dir),
            )
        )
        assert response is not None

        yield client, response

        await client.shutdown_async(None)
        client.exit(None)

        await client.stop()

    return fixture_func
