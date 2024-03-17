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
async def goto(get_client_for):
    async for result in get_client_for("goto.py"):
        yield result


async def test_definition(
    goto: Tuple[BaseLanguageClient, types.InitializeResult], path_for, uri_for
):
    """Ensure that we can implement type definition requests."""
    client, initialize_result = goto

    definition_options = initialize_result.capabilities.definition_provider
    assert definition_options is True

    test_uri = uri_for("code.txt")
    test_path = path_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                text=test_path.read_text(),
            )
        )
    )

    response = await client.text_document_definition_async(
        types.DefinitionParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            position=types.Position(line=6, character=47),
        )
    )
    assert response is None

    response = await client.text_document_definition_async(
        types.DefinitionParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            position=types.Position(line=5, character=20),
        )
    )
    assert isinstance(response, types.Location)
    assert response.uri == test_uri
    assert response.range == types.Range(
        start=types.Position(line=0, character=5),
        end=types.Position(line=0, character=14),
    )
