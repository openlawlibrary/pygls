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
async def colors(get_client_for):
    async for result in get_client_for("colors.py"):
        yield result


def range_from_str(range_: str) -> types.Range:
    start, end = range_.split("-")
    start_line, start_char = start.split(":")
    end_line, end_char = end.split(":")

    return types.Range(
        start=types.Position(line=int(start_line), character=int(start_char)),
        end=types.Position(line=int(end_line), character=int(end_char)),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_color(
    colors: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example colors server is working as expected."""
    client, initialize_result = colors

    colors_options = initialize_result.capabilities.color_provider
    assert colors_options is True

    test_uri = uri_for("colors.txt")
    response = await client.text_document_document_color_async(
        types.DocumentColorParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri)
        )
    )

    assert tuple(response) == (
        types.ColorInformation(
            range=range_from_str("0:7-0:14"),
            color=types.Color(red=1.0, green=0.0, blue=0.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("0:24-0:31"),
            color=types.Color(red=0.0, green=1.0, blue=0.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("0:44-0:51"),
            color=types.Color(red=0.0, green=0.0, blue=1.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("3:7-3:14"),
            color=types.Color(red=1.0, green=1.0, blue=0.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("5:5-5:12"),
            color=types.Color(red=1.0, green=0.0, blue=1.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("7:5-7:12"),
            color=types.Color(red=0.0, green=1.0, blue=1.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("9:43-9:47"),
            color=types.Color(red=1.0, green=0.0, blue=0.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("9:49-9:53"),
            color=types.Color(red=0.0, green=1.0, blue=0.0, alpha=1.0),
        ),
        types.ColorInformation(
            range=range_from_str("9:55-9:59"),
            color=types.Color(red=0.0, green=0.0, blue=1.0, alpha=1.0),
        ),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_color_presentation(
    colors: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the server can convert colors to their string representation
    correctly."""

    client, _ = colors

    test_uri = uri_for("colors.txt")
    response = await client.text_document_color_presentation_async(
        types.ColorPresentationParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            color=types.Color(red=0.25, green=0.5, blue=0.75, alpha=1.0),
            range=range_from_str("0:7-0:14"),
        )
    )

    assert tuple(response) == (types.ColorPresentation(label="#3f7fbf"),)
