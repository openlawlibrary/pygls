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
async def formatting(get_client_for):
    async for result in get_client_for("formatting.py"):
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
async def test_document_format(
    formatting: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example document format server method is working as expected."""
    client, initialize_result = formatting

    format_options = initialize_result.capabilities.document_formatting_provider
    assert format_options is True

    test_uri = uri_for("table.txt")
    response = await client.text_document_formatting_async(
        types.DocumentFormattingParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            options=types.FormattingOptions(tab_size=4, insert_spaces=True),
        )
    )

    assert tuple(response) == (
        types.TextEdit(
            new_text="|   a   |   b    |\n", range=range_from_str("0:0-1:0")
        ),
        types.TextEdit(
            new_text="|-------|--------|\n", range=range_from_str("1:0-2:0")
        ),
        types.TextEdit(
            new_text="| apple | banana |\n", range=range_from_str("2:0-3:0")
        ),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_range_format_one(
    formatting: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example range format server method is working as expected."""
    client, initialize_result = formatting

    format_options = initialize_result.capabilities.document_range_formatting_provider
    assert format_options is True

    test_uri = uri_for("table.txt")
    response = await client.text_document_range_formatting_async(
        types.DocumentRangeFormattingParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            options=types.FormattingOptions(tab_size=4, insert_spaces=True),
            range=range_from_str("0:0-1:5"),
        )
    )

    assert tuple(response) == (
        types.TextEdit(new_text="| a | b |\n", range=range_from_str("0:0-1:0")),
        types.TextEdit(new_text="|---|---|\n", range=range_from_str("1:0-2:0")),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_range_format_two(
    formatting: Tuple[BaseLanguageClient, types.InitializeResult], uri_for
):
    """Ensure that the example range format server method is working as expected."""
    client, initialize_result = formatting

    format_options = initialize_result.capabilities.document_range_formatting_provider
    assert format_options is True

    test_uri = uri_for("table.txt")
    response = await client.text_document_range_formatting_async(
        types.DocumentRangeFormattingParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            options=types.FormattingOptions(tab_size=4, insert_spaces=True),
            range=range_from_str("1:0-2:14"),
        )
    )

    assert tuple(response) == (
        types.TextEdit(
            new_text="|-------|--------|\n", range=range_from_str("1:0-2:0")
        ),
        types.TextEdit(
            new_text="| apple | banana |\n", range=range_from_str("2:0-3:0")
        ),
    )


@pytest.mark.asyncio(loop_scope="module")
async def test_document_on_type_format(
    formatting: Tuple[BaseLanguageClient, types.InitializeResult], path_for, uri_for
):
    """Ensure that the example on type format server method is working as expected."""
    client, initialize_result = formatting

    format_options = initialize_result.capabilities.document_on_type_formatting_provider
    assert format_options == types.DocumentOnTypeFormattingOptions(
        first_trigger_character="|"
    )

    test_path = path_for("table.txt")
    test_uri = uri_for("table.txt")

    # Open and replace the contents of the table.txt file.
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

    client.text_document_did_change(
        types.DidChangeTextDocumentParams(
            text_document=types.VersionedTextDocumentIdentifier(
                uri=test_uri, version=1
            ),
            content_changes=[
                types.TextDocumentContentChangePartial(
                    text="|header one| header two |\n|-|",
                    range=range_from_str("0:0-3:0"),
                )
            ],
        )
    )

    # Ask the server to format the recently typed text.
    response = await client.text_document_on_type_formatting_async(
        types.DocumentOnTypeFormattingParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
            position=types.Position(line=1, character=2),
            ch="|",
            options=types.FormattingOptions(tab_size=4, insert_spaces=True),
        )
    )

    assert tuple(response) == (
        types.TextEdit(
            new_text="| header one | header two |\n", range=range_from_str("0:0-1:0")
        ),
        types.TextEdit(
            new_text="|------------|------------|\n", range=range_from_str("1:0-2:0")
        ),
    )
