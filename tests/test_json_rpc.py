#############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
#############################################################################
"""Regression tests for outgoing JSON-RPC request cleanup and late responses."""
import asyncio
import io
from concurrent.futures import Future

import pytest
from lsprotocol.types import ResponseError

from pygls.protocol import default_converter
from pygls.protocol.json_rpc import JsonRPCProtocol


def _make_protocol() -> JsonRPCProtocol:
    """Build a protocol without running __init__ (no server needed):
    _handle_response only touches _request_futures."""
    protocol = JsonRPCProtocol.__new__(JsonRPCProtocol)
    protocol._request_futures = {}
    protocol._result_types = {}
    return protocol


def test_response_to_cancelled_request_future_is_ignored():
    protocol = _make_protocol()
    future: Future = Future()
    protocol._request_futures[1] = future
    # The awaiting task got cancelled (e.g. a debounced server->client request).
    assert future.cancel()

    # A late response must not raise InvalidStateError.
    protocol._handle_response(1, result={"ok": True})
    # ...and the bookkeeping entry must be cleaned up.
    assert 1 not in protocol._request_futures


def test_error_response_to_cancelled_request_future_is_ignored():
    protocol = _make_protocol()
    future: Future = Future()
    protocol._request_futures[2] = future
    assert future.cancel()

    # Error responses go through the same path via set_exception.
    protocol._handle_response(
        2, error=ResponseError(code=-32601, message="method not found")
    )
    assert 2 not in protocol._request_futures


def test_response_to_unknown_message_id_still_warns_not_raises():
    protocol = _make_protocol()
    # Existing behaviour: unknown ids are ignored (warning only).
    protocol._handle_response(99, result={"ok": True})
    assert protocol._request_futures == {}


def test_cancelled_outgoing_request_releases_bookkeeping():
    protocol = JsonRPCProtocol(None, default_converter())
    protocol.set_writer(io.BytesIO(), include_headers=False)

    future = protocol.send_request("test/request", msg_id=1)
    assert 1 in protocol._request_futures
    assert 1 in protocol._result_types

    assert future.cancel()
    assert protocol._request_futures == {}
    assert protocol._result_types == {}


@pytest.mark.asyncio
async def test_cancelled_async_request_releases_bookkeeping():
    protocol = JsonRPCProtocol(None, default_converter())
    protocol.set_writer(io.BytesIO(), include_headers=False)

    future = protocol.send_request_async("test/request", msg_id=1)
    assert future.cancel()
    with pytest.raises(asyncio.CancelledError):
        await future
    await asyncio.sleep(0)

    assert protocol._request_futures == {}
    assert protocol._result_types == {}


def test_failed_outgoing_request_releases_bookkeeping():
    protocol = JsonRPCProtocol(None, default_converter())
    protocol.set_writer(io.BytesIO(), include_headers=False)

    future = protocol.send_request("test/request", msg_id=1)
    response = protocol.structure_message(
        {"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "missing"}}
    )
    protocol.handle_message(response)

    assert future.done()
    assert protocol._request_futures == {}
    assert protocol._result_types == {}
