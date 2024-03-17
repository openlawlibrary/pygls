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
async def inlay_hints(get_client_for):
    async for result in get_client_for("inlay_hints.py"):
        yield result


async def test_inlay_hints(
    inlay_hints: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example code action server is working as expected."""
    client, initialize_result = inlay_hints

    inlay_hint_provider = initialize_result.capabilities.inlay_hint_provider
    assert inlay_hint_provider.resolve_provider is True

    test_uri = uri_for("sums.txt")
    assert test_uri is not None

    response = await client.text_document_inlay_hint_async(
        types.InlayHintParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            range=types.Range(
                start=types.Position(line=3, character=0),
                end=types.Position(line=4, character=0),
            ),
        )
    )

    assert len(response) == 2
    two, three = response[0], response[1]

    assert two.label == ":10"
    assert two.tooltip is None

    assert three.label == ":11"
    assert three.tooltip is None

    resolved = await client.inlay_hint_resolve_async(three)
    assert resolved.tooltip == "Binary representation of the number: 3"
