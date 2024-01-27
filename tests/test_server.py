import asyncio
import pathlib
import sys
from unittest import mock

import pytest

from pygls.client import JsonRPCClient

SERVERS = pathlib.Path(__file__).parent / "servers"


@pytest.fixture(scope="module")
async def client():
    client_ = JsonRPCClient()
    await client_.start_io(sys.executable, str(SERVERS / "rpc.py"))

    yield client_

    await client_.stop()


async def test_send_request_sync(client: JsonRPCClient):
    """Ensure that we can send a request and handle the result using a callback."""

    callback = mock.Mock()

    # TODO: How to wait, without requiring await
    await asyncio.wait_for(
        client.send_request("math/add", dict(a=2, b=2), callback=callback), timeout=10
    )

    callback.assert_called_with(dict(sum=4))


async def test_send_request_async(client: JsonRPCClient):
    """Ensure that we can send a request and handle the result using async-await syntax."""

    result = await client.send_request("math/add", dict(a=1, b=4))
    assert result["sum"] == 5
