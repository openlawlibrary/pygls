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

import logging
import itertools
import typing

import pytest
import pytest_asyncio
from lsprotocol import types

from pygls.exceptions import JsonRpcInternalError, JsonRpcInvalidParams

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import LanguageClient


logger = logging.getLogger(__name__)


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def commands(get_client_for):
    async for result in get_client_for("commands.py"):
        client, _ = result

        @client.feature(types.WINDOW_LOG_MESSAGE)
        def log(params: types.LogMessageParams):
            logger.info(params.message)

        yield result


@pytest.mark.asyncio(loop_scope="module")
async def test_command_not_defined(
    commands: Tuple[LanguageClient, types.InitializeResult]
):
    """Ensure that the example commands server handles the case where
    the requested command is not defined."""

    client, _ = commands

    with pytest.raises(
        JsonRpcInvalidParams,
        match="Invalid Params: Command name 'not.defined' is not defined",
    ):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(
                command="not.defined",
            )
        )


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("name", ["random", "random.wrapped"])
async def test_random(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server can execute both the wrapped and
    unwrapped ``calculate.triangle.hypotenuse`` commands correctly."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    result = await client.workspace_execute_command_async(
        types.ExecuteCommandParams(
            command=name,
            arguments=None,
        )
    )

    assert result == 4


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("name", ["random", "random.wrapped"])
async def test_random_invalid(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server handles the case when a command is called
    with too many arguments."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    with pytest.raises(
        JsonRpcInvalidParams, match="Invalid Params: Expected 0 arguments, got 1"
    ):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(
                command=name,
                arguments=[{"seed": 1234}],
            )
        )


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "name, setup",
    [
        *itertools.product(
            ["calculate.sum", "calculate.sum.wrapped"],
            [
                ([], 0),
                ([1], 1),
                ([1, 2], 3),
                ([1, 2, 3], 6),
            ],
        ),
    ],
)
async def test_calculate_sum(
    commands: Tuple[LanguageClient, types.InitializeResult],
    name: str,
    setup: tuple[list[int], int],
):
    """Ensure that the example commands server can execute both the wrapped and
    unwrapped ``calculate.sum`` commands correctly."""

    client, initialize_result = commands
    arguments, expected = setup

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    result = await client.workspace_execute_command_async(
        types.ExecuteCommandParams(
            command=name,
            arguments=arguments,
        )
    )

    assert result == expected


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("name", ["calculate.pow", "calculate.pow.wrapped"])
async def test_calculate_pow_invalid(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server handles the case where not enough
    arguments are given."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    with pytest.raises(
        JsonRpcInvalidParams, match="Invalid Params: Expected 2 arguments, got 1"
    ):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(
                command=name,
                arguments=[3],
            )
        )


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "name",
    [
        "calculate.pow",
        "calculate.pow.async",
        "calculate.pow.wrapped",
        "calculate.pow.async.wrapped",
    ],
)
async def test_calculate_pow(
    commands: Tuple[LanguageClient, types.InitializeResult],
    name: str,
    runtime: str,
):
    """Ensure that the example commands server can execute both the wrapped and
    unwrapped ``calculate.pow`` commands correctly."""

    if runtime in {"pyodide"} and "async" in name:
        pytest.skip("async handlers not supported in this runtime")

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    result = await client.workspace_execute_command_async(
        types.ExecuteCommandParams(
            command=name,
            arguments=[2, 3],
        )
    )

    assert result == 8


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize("name", ["calculate.div", "calculate.div.wrapped"])
async def test_calculate_div_invalid(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server handles the case where
    there is a error in the command handler."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    with pytest.raises(
        JsonRpcInternalError, match="ZeroDivisionError:.*division by zero"
    ):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(
                command=name,
                arguments=[3, 0],
            )
        )


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "name",
    ["calculate.div", "calculate.div.wrapped"],
)
async def test_calculate_div(
    commands: Tuple[LanguageClient, types.InitializeResult],
    name: str,
):
    """Ensure that the example commands server can execute both the wrapped and
    unwrapped ``calculate.pow`` commands correctly."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    result = await client.workspace_execute_command_async(
        types.ExecuteCommandParams(
            command=name,
            arguments=[6, 3],
        )
    )

    assert result == 2


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "name",
    [
        "calculate.triangle.hypotenuse",
        "calculate.triangle.hypotenuse.wrapped",
        "calculate.untyped.hypotenuse",
        "calculate.untyped.hypotenuse.wrapped",
    ],
)
async def test_calculate_hypotenuse(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server can execute both the wrapped and
    unwrapped ``calculate.triangle.hypotenuse`` commands correctly."""

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    result = await client.workspace_execute_command_async(
        types.ExecuteCommandParams(
            command=name,
            arguments=[{"a": 3, "b": 4}],
        )
    )

    assert result == {"a": 3, "b": 4, "c": 5}


@pytest.mark.asyncio(loop_scope="module")
@pytest.mark.parametrize(
    "name",
    [
        "calculate.triangle.hypotenuse",
        "calculate.triangle.hypotenuse.wrapped",
    ],
)
async def test_calculate_hypotenuse_invalid(
    commands: Tuple[LanguageClient, types.InitializeResult], name: str
):
    """Ensure that the example commands server handles the case where the given argument
    does not align to the expected type
    """

    client, initialize_result = commands

    provider = initialize_result.capabilities.execute_command_provider
    assert name in provider.commands

    with pytest.raises(
        JsonRpcInvalidParams, match="Invalid Params: While structuring Triangle.*"
    ):
        await client.workspace_execute_command_async(
            types.ExecuteCommandParams(
                command=name,
                arguments=[{"x": 3, "y": 4}],
            )
        )
