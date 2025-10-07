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

import asyncio
from collections.abc import Sequence
import time
import typing
from functools import partial

import pytest
import pytest_asyncio
import cattrs
from lsprotocol import types

from pygls import IS_WIN
from pygls.exceptions import JsonRpcInternalError

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture(scope="function", loop_scope="function")
async def threaded_handlers(get_client_for):
    async for result in get_client_for("threaded_handlers.py"):
        client, _ = result

        # Add a handler to capture window/showMessage notifications
        client.messages = []

        @client.feature(types.WINDOW_SHOW_MESSAGE)
        def _(params):
            client.messages.append(params)

        yield result


def record_time(result, *, timedict, key):
    """Record the time at which the given result was received."""
    timedict[key] = time.perf_counter()
    return result


@pytest.mark.asyncio(loop_scope="function")
async def test_countdown_blocking(
    threaded_handlers: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the countdown blocking command is working as expected."""
    client, initialize_result = threaded_handlers

    completion_options = initialize_result.capabilities.completion_provider
    # https://catt.rs/en/latest/migrations.html#sequences-structuring-into-tuples
    seq = type(cattrs.structure([], Sequence[str]))
    assert completion_options == types.CompletionOptions(trigger_characters=seq((".",)))

    command_provider = initialize_result.capabilities.execute_command_provider
    assert tuple(command_provider.commands) == (
        "count.down.blocking",
        "count.down.thread",
        "count.down.error",
    )

    test_uri = uri_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                # For the purpose of this test, let's lie about the file's contents
                text=".",
            )
        )
    )

    times = {}
    command_task = asyncio.ensure_future(
        client.workspace_execute_command_async(
            types.ExecuteCommandParams(command="count.down.blocking")
        )
    )
    command_task.add_done_callback(partial(record_time, timedict=times, key="command"))

    completion_task = asyncio.ensure_future(
        client.text_document_completion_async(
            types.CompletionParams(
                text_document=types.TextDocumentIdentifier(uri=test_uri),
                position=types.Position(line=0, character=1),
            )
        )
    )
    completion_task.add_done_callback(
        partial(record_time, timedict=times, key="completion")
    )

    command_result, completions = await asyncio.gather(command_task, completion_task)

    # check the results are as expected
    assert command_result is None
    assert {"one", "two", "three", "four", "five"} == {
        c.label for c in completions.items
    }

    # check we recevied the expected messages
    assert len(messages := [m.message for m in client.messages]) == 10
    assert all(m.startswith("Counting down in thread 'MainThread'") for m in messages)

    # crucially, the completions should have been blocked by the countdown and therefore
    # finish second
    assert times["command"] < times["completion"]


@pytest.mark.asyncio(loop_scope="function")
async def test_countdown_threaded(
    threaded_handlers: Tuple[BaseLanguageClient, types.InitializeResult],
    uri_for,
    runtime: str,
    transport: str,
):
    """Ensure that the countdown threaded command is working as expected."""

    if runtime == "pyodide":
        pytest.skip("threads not supported in pyodide")

    if (IS_WIN and transport == "tcp") or transport == "websockets":
        pytest.skip("see https://github.com/openlawlibrary/pygls/issues/502")

    client, initialize_result = threaded_handlers

    completion_options = initialize_result.capabilities.completion_provider
    # https://catt.rs/en/latest/migrations.html#sequences-structuring-into-tuples
    seq = type(cattrs.structure([], Sequence[str]))
    assert completion_options == types.CompletionOptions(trigger_characters=seq((".",)))

    command_provider = initialize_result.capabilities.execute_command_provider
    assert tuple(command_provider.commands) == (
        "count.down.blocking",
        "count.down.thread",
        "count.down.error",
    )

    test_uri = uri_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                # For the purpose of this test, let's lie about the file's contents
                text=".",
            )
        )
    )

    times = {}
    command_task = asyncio.ensure_future(
        client.workspace_execute_command_async(
            types.ExecuteCommandParams(command="count.down.thread")
        )
    )
    command_task.add_done_callback(partial(record_time, timedict=times, key="command"))

    completion_task = asyncio.ensure_future(
        client.text_document_completion_async(
            types.CompletionParams(
                text_document=types.TextDocumentIdentifier(uri=test_uri),
                position=types.Position(line=0, character=1),
            )
        )
    )
    completion_task.add_done_callback(
        partial(record_time, timedict=times, key="completion")
    )

    command_result, completions = await asyncio.gather(command_task, completion_task)

    # check the results are as expected
    assert command_result is None
    assert {"one", "two", "three", "four", "five"} == {
        c.label for c in completions.items
    }

    # check we recevied the expected messages
    assert len(messages := [m.message for m in client.messages]) == 10
    assert all(m.startswith("Counting down in thread 'ThreadPool") for m in messages)

    # crucially, the completions should NOT have been blocked by the
    # countdown and therefore finish first
    assert times["completion"] < times["command"]


@pytest.mark.asyncio(loop_scope="function")
async def test_countdown_error(
    threaded_handlers: Tuple[BaseLanguageClient, types.InitializeResult],
    uri_for,
    runtime: str,
):
    """Ensure that errors raised in threaded handlers are still handled correctly."""

    if runtime == "pyodide":
        pytest.skip("threads not supported in pyodide")

    client, initialize_result = threaded_handlers

    completion_options = initialize_result.capabilities.completion_provider
    # https://catt.rs/en/latest/migrations.html#sequences-structuring-into-tuples
    seq = type(cattrs.structure([], Sequence[str]))
    assert completion_options == types.CompletionOptions(trigger_characters=seq((".",)))

    command_provider = initialize_result.capabilities.execute_command_provider
    assert tuple(command_provider.commands) == (
        "count.down.blocking",
        "count.down.thread",
        "count.down.error",
    )

    with pytest.raises(JsonRpcInternalError, match="ZeroDivisionError"):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(command="count.down.error")
        )
