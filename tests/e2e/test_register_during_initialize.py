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

import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture()
async def without_formatting(get_client_for):
    async for result in get_client_for("register_during_initialize.py"):
        yield result


async def test_without_formatting(
    without_formatting: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the formatting provider is not set by default."""
    client, initialize_result = without_formatting

    format_options = initialize_result.capabilities.document_formatting_provider
    assert format_options is None


@pytest_asyncio.fixture()
async def with_formatting(get_client_for):
    init_options = {"formatting": True}

    async for result in get_client_for(
        "register_during_initialize.py", initialization_options=init_options
    ):
        yield result


async def test_with_formatting(
    with_formatting: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the formatting provider is present when requested."""
    client, initialize_result = with_formatting

    format_options = initialize_result.capabilities.document_formatting_provider
    assert format_options is not None
