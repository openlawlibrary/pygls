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
from __future__ import annotations

import typing

import pytest
import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture()
async def async_shutdown(runtime: str, get_client_for):
    if runtime in {"pyodide"}:
        pytest.skip("async handlers not supported in this runtime")

    async for result in get_client_for("async_shutdown.py", auto_shutdown=False):
        client = result[0]
        client.log_messages = []

        @client.feature(types.WINDOW_LOG_MESSAGE)
        def _(params: types.LogMessageParams):
            client.log_messages.append(params.message)

        yield result


async def test_async_shutdown(
    async_shutdown: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the formatting provider is not set by default."""
    client, _ = async_shutdown

    await client.shutdown_async(None)
    client.exit(None)

    assert client.log_messages[0] == "Shutdown started"
    assert client.log_messages[1] == "Shutdown complete"
