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
"""Regression tests for issue #621: a response arriving after its request
future was cancelled must not crash the message handler with
``InvalidStateError``."""
from concurrent.futures import Future

from lsprotocol.types import ResponseError

from pygls.protocol.json_rpc import JsonRPCProtocol


def _make_protocol() -> JsonRPCProtocol:
    """Build a protocol without running __init__ (no server needed):
    _handle_response only touches _request_futures."""
    protocol = JsonRPCProtocol.__new__(JsonRPCProtocol)
    protocol._request_futures = {}
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
