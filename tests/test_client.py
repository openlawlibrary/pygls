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
import pathlib
import sys

import pytest

from pygls.client import JsonRPCClient

SERVERS = pathlib.Path(__file__).parent / "servers"


@pytest.mark.asyncio
async def test_client_detect_server_exit():
    """Ensure that the client detects when the server process exits."""

    class TestClient(JsonRPCClient):
        server_exit_called = False

        async def server_exit(self, server: asyncio.subprocess.Process):
            self.server_exit_called = True
            assert server.returncode == 0

    client = TestClient()
    await client.start_io(sys.executable, "-c", "print('Hello, World!')")
    await asyncio.sleep(1)
    await client.stop()

    message = "Expected the `server_exit` method to have been called."
    assert client.server_exit_called, message


@pytest.mark.asyncio
async def test_client_detect_invalid_json():
    """Ensure that the client can detect the case where the server returns invalid
    json."""

    class TestClient(JsonRPCClient):
        report_error_called = False
        future = None

        def error_handler(self, error: Exception):
            self.report_error_called = True
            assert "Unterminated string" in str(error)

    client = TestClient()
    await client.start_io(sys.executable, str(SERVERS / "invalid_json.py"))

    cancelled = False
    try:
        await asyncio.wait_for(
            client.send_request("method/name", {}), timeout=5.0  # seconds
        )
    except asyncio.TimeoutError:
        assert_message = "Expected `error_handler` to have been called"
        assert client.report_error_called, assert_message
        cancelled = True

    assert cancelled is True, "Expected request to have been cancelled."


@pytest.mark.asyncio
async def test_client_large_responses():
    """Ensure that the client can correctly handle large responses from a server."""

    client = JsonRPCClient()
    await client.start_io(sys.executable, str(SERVERS / "large_response.py"))

    result = await client.send_request("get/numbers", {}, msg_id=1)
    assert len(result["numbers"]) == 100_000

    await client.stop()
