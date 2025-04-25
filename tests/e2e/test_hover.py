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
    from typing import List
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def hover(get_client_for):
    async for result in get_client_for("hover.py"):
        yield result


@pytest.mark.parametrize(
    "position, expected",
    [
        (
            types.Position(line=0, character=3),
            "\n".join(
                [
                    "# Sat 01 Feb 2020",
                    "",
                    "| Format | Value |",
                    "|:-|-:|",
                    "| `%H:%M:%S` | 00:00:00 |",
                    "| `%d/%m/%y` | 01/02/20 |",
                    "| `%Y-%m-%d` | 2020-02-01 |",
                    "| `%Y-%m-%dT%H:%M:%S` | 2020-02-01T00:00:00 |",
                ]
            ),
        ),
        (types.Position(line=1, character=3), None),
        (
            types.Position(line=2, character=3),
            "\n".join(
                [
                    "# Sun 02 Jan 1921",
                    "",
                    "| Format | Value |",
                    "|:-|-:|",
                    "| `%H:%M:%S` | 23:59:00 |",
                    "| `%d/%m/%y` | 02/01/21 |",
                    "| `%Y-%m-%d` | 1921-01-02 |",
                    "| `%Y-%m-%dT%H:%M:%S` | 1921-01-02T23:59:00 |",
                ]
            ),
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="module")
async def test_hover(
    hover: Tuple[BaseLanguageClient, types.InitializeResult],
    uri_for,
    position: types.Position,
    expected: List[str],
):
    """Ensure that the example hover server is working as expected."""
    client, initialize_result = hover

    hover_options = initialize_result.capabilities.hover_provider
    assert hover_options is True

    test_uri = uri_for("dates.txt")
    response = await client.text_document_hover_async(
        types.HoverParams(
            position=position,
            text_document=types.TextDocumentIdentifier(uri=test_uri),
        )
    )

    if expected is None:
        assert response is None
        return

    assert response == types.Hover(
        contents=types.MarkupContent(
            kind=types.MarkupKind.Markdown,
            value=expected,
        ),
        range=types.Range(
            start=types.Position(line=position.line, character=0),
            end=types.Position(line=position.line + 1, character=0),
        ),
    )
