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


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def semantic_tokens(get_client_for):
    async for result in get_client_for("semantic_tokens.py"):
        yield result


@pytest.mark.parametrize(
    "text,expected",
    [
        # Just a handful of cases to check we've got the basics right
        ("fn", (0, 0, 2, 0, 0)),
        ("type", (0, 0, 4, 0, 0)),
        ("Rectangle", (0, 0, 9, 5, 0)),
        (
            "type Rectangle",
            (
                # fmt: off
            0, 0, 4, 0, 0,
            0, 5, 9, 5, 8,
                # fmt: on
            ),
        ),
        (
            "fn area",
            (
                # fmt: off
            0, 0, 2, 0, 0,
            0, 3, 4, 2, 8,
                # fmt: on
            ),
        ),
        (
            "fn\n area",
            (
                # fmt: off
            0, 0, 2, 0, 0,
            1, 1, 4, 2, 8,
                # fmt: on
            ),
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="module")
async def test_semantic_tokens_full(
    semantic_tokens: Tuple[BaseLanguageClient, types.InitializeResult],
    uri_for,
    path_for,
    text: str,
    expected: Tuple[int],
):
    """Ensure that the example semantic tokens server is working as expected."""
    client, initialize_result = semantic_tokens

    semantic_tokens_options = initialize_result.capabilities.semantic_tokens_provider
    assert semantic_tokens_options.full is True

    legend = semantic_tokens_options.legend
    assert tuple(legend.token_types) == (
        "keyword",
        "variable",
        "function",
        "operator",
        "parameter",
        "type",
    )
    assert tuple(legend.token_modifiers) == (
        "deprecated",
        "readonly",
        "defaultLibrary",
        "definition",
    )

    test_uri = uri_for("code.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                text=text,
            )
        )
    )

    response = await client.text_document_semantic_tokens_full_async(
        types.SemanticTokensParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
        )
    )
    assert tuple(response.data) == expected
