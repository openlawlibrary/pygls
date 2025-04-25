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
async def symbols(get_client_for):
    async for result in get_client_for("symbols.py"):
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
async def test_document_symbols(
    symbols: Tuple[BaseLanguageClient, types.InitializeResult], uri_for, path_for
):
    """Ensure that the example symbols server is working as expected."""
    client, initialize_result = symbols

    document_symbols_options = initialize_result.capabilities.document_symbol_provider
    assert document_symbols_options is True

    test_uri = uri_for("code.txt")
    test_path = path_for("code.txt")

    # Needed so that the server parses the document
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

    expected = [
        types.DocumentSymbol(
            name="Rectangle",
            kind=types.SymbolKind.Class,
            range=range_from_str("0:0-1:0"),
            selection_range=range_from_str("0:5-0:14"),
            children=[
                types.DocumentSymbol(
                    name="x",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("0:15-0:16"),
                    selection_range=range_from_str("0:15-0:16"),
                ),
                types.DocumentSymbol(
                    name="y",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("0:18-0:19"),
                    selection_range=range_from_str("0:18-0:19"),
                ),
                types.DocumentSymbol(
                    name="w",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("0:21-0:22"),
                    selection_range=range_from_str("0:21-0:22"),
                ),
                types.DocumentSymbol(
                    name="h",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("0:24-0:25"),
                    selection_range=range_from_str("0:24-0:25"),
                ),
            ],
        ),
        types.DocumentSymbol(
            name="Square",
            kind=types.SymbolKind.Class,
            range=range_from_str("1:0-2:0"),
            selection_range=range_from_str("1:5-1:11"),
            children=[
                types.DocumentSymbol(
                    name="x",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("1:12-1:13"),
                    selection_range=range_from_str("1:12-1:13"),
                ),
                types.DocumentSymbol(
                    name="y",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("1:15-1:16"),
                    selection_range=range_from_str("1:15-1:16"),
                ),
                types.DocumentSymbol(
                    name="s",
                    kind=types.SymbolKind.Field,
                    range=range_from_str("1:18-1:19"),
                    selection_range=range_from_str("1:18-1:19"),
                ),
            ],
        ),
        types.DocumentSymbol(
            name="area",
            kind=types.SymbolKind.Function,
            range=range_from_str("3:0-4:0"),
            selection_range=range_from_str("3:3-3:7"),
            children=[
                types.DocumentSymbol(
                    name="rect",
                    kind=types.SymbolKind.Variable,
                    range=range_from_str("3:8-3:12"),
                    selection_range=range_from_str("3:8-3:12"),
                ),
            ],
        ),
        types.DocumentSymbol(
            name="volume",
            kind=types.SymbolKind.Function,
            range=range_from_str("5:0-6:0"),
            selection_range=range_from_str("5:3-5:9"),
            children=[
                types.DocumentSymbol(
                    name="rect",
                    kind=types.SymbolKind.Variable,
                    range=range_from_str("5:10-5:14"),
                    selection_range=range_from_str("5:10-5:14"),
                ),
                types.DocumentSymbol(
                    name="length",
                    kind=types.SymbolKind.Variable,
                    range=range_from_str("5:27-5:33"),
                    selection_range=range_from_str("5:27-5:33"),
                ),
            ],
        ),
    ]

    response = await client.text_document_document_symbol_async(
        types.DocumentSymbolParams(
            text_document=types.TextDocumentIdentifier(uri=test_uri),
        ),
    )
    assert len(response) == len(expected)
    for expected_symbol, actual_symbol in zip(expected, response):
        check_document_symbol(expected_symbol, actual_symbol)


@pytest.mark.parametrize(
    "query, expected",
    [
        (
            "",
            [
                types.SymbolInformation(
                    name="Rectangle",
                    kind=types.SymbolKind.Class,
                    location=types.Location(uri="", range=range_from_str("0:5-0:14")),
                ),
                types.SymbolInformation(
                    name="x",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("0:15-0:16")),
                    container_name="Rectangle",
                ),
                types.SymbolInformation(
                    name="y",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("0:18-0:19")),
                    container_name="Rectangle",
                ),
                types.SymbolInformation(
                    name="w",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("0:21-0:22")),
                    container_name="Rectangle",
                ),
                types.SymbolInformation(
                    name="h",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("0:24-0:25")),
                    container_name="Rectangle",
                ),
                types.SymbolInformation(
                    name="Square",
                    kind=types.SymbolKind.Class,
                    location=types.Location(uri="", range=range_from_str("1:5-1:11")),
                ),
                types.SymbolInformation(
                    name="x",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("1:12-1:13")),
                    container_name="Square",
                ),
                types.SymbolInformation(
                    name="y",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("1:15-1:16")),
                    container_name="Square",
                ),
                types.SymbolInformation(
                    name="s",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("1:18-1:19")),
                    container_name="Square",
                ),
                types.SymbolInformation(
                    name="area",
                    kind=types.SymbolKind.Function,
                    location=types.Location(uri="", range=range_from_str("3:3-3:7")),
                ),
                types.SymbolInformation(
                    name="rect",
                    kind=types.SymbolKind.Variable,
                    location=types.Location(uri="", range=range_from_str("3:8-3:12")),
                    container_name="area",
                ),
                types.SymbolInformation(
                    name="volume",
                    kind=types.SymbolKind.Function,
                    location=types.Location(uri="", range=range_from_str("5:3-5:9")),
                ),
                types.SymbolInformation(
                    name="rect",
                    kind=types.SymbolKind.Variable,
                    location=types.Location(uri="", range=range_from_str("5:10-5:14")),
                    container_name="volume",
                ),
                types.SymbolInformation(
                    name="length",
                    kind=types.SymbolKind.Variable,
                    location=types.Location(uri="", range=range_from_str("5:27-5:33")),
                    container_name="volume",
                ),
            ],
        ),
        (
            "x",
            [
                types.SymbolInformation(
                    name="x",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("0:15-0:16")),
                    container_name="Rectangle",
                ),
                types.SymbolInformation(
                    name="x",
                    kind=types.SymbolKind.Field,
                    location=types.Location(uri="", range=range_from_str("1:12-1:13")),
                    container_name="Square",
                ),
            ],
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="module")
async def test_workspace_symbols(
    symbols: Tuple[BaseLanguageClient, types.InitializeResult],
    uri_for,
    path_for,
    query,
    expected,
):
    """Ensure that the example symbols server is working as expected."""
    client, initialize_result = symbols

    document_symbols_options = initialize_result.capabilities.document_symbol_provider
    assert document_symbols_options is True

    test_uri = uri_for("code.txt")
    test_path = path_for("code.txt")

    # Needed so that the server parses the document
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

    response = await client.workspace_symbol_async(
        types.WorkspaceSymbolParams(query=query),
    )

    assert len(response) == len(expected)
    for expected_symbol, actual_symbol in zip(expected, response):
        expected_symbol.location.uri = test_uri

        assert expected_symbol == actual_symbol


def check_document_symbol(actual: types.DocumentSymbol, expected: types.DocumentSymbol):
    """Ensure that the given ``DocumentSymbols`` are equivalent."""

    assert isinstance(actual, types.DocumentSymbol)

    assert actual.name == expected.name
    assert actual.kind == expected.kind
    assert actual.range == expected.range
    assert actual.selection_range == expected.selection_range

    if expected.children is None:
        assert actual.children is None
        return

    assert actual.children is not None
    assert len(actual.children) == len(
        expected.children
    ), f"Children mismatch in symbol '{actual.name}'"

    for actual_child, expected_child in zip(actual.children, expected.children):
        check_document_symbol(actual_child, expected_child)
