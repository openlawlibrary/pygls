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
"""This implements the various formatting requests from the specification

- :lsp:`textDocument/formatting`: format the entire document.
- :lsp:`textDocument/rangeFormatting`: format just the given range within a document.
- :lsp:`textDocument/onTypeFormatting`: format the document while the user is actively
  typing.

These are typically invoked by the client when the user asks their editor to format the
document or as part of automatic triggers (e.g. format on save).
Depending on the client, the user may need to do some additional configuration to enable
some of these methods e.g. setting ``editor.formatOnType`` in VSCode to enable
``textDocument/onTypeFormatting``.

This server implements basic formatting of Markdown style tables.

The implementation is a little buggy in that the resulting table might not be what you
expect (fixes welcome!), but it should be enough to demonstrate the expected interaction
between client and server.
"""

import logging
from typing import Dict
from typing import List
from typing import Optional

import attrs
from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument


@attrs.define
class Row:
    """Represents a row in the table"""

    cells: List[str]
    cell_widths: List[int]
    line_number: int


server = LanguageServer("formatting-server", "v1")


@server.feature(types.TEXT_DOCUMENT_FORMATTING)
def format_document(ls: LanguageServer, params: types.DocumentFormattingParams):
    """Format the entire document"""
    logging.debug("%s", params)

    doc = ls.workspace.get_text_document(params.text_document.uri)
    rows = parse_document(doc)
    return format_table(rows)


@server.feature(types.TEXT_DOCUMENT_RANGE_FORMATTING)
def format_range(ls: LanguageServer, params: types.DocumentRangeFormattingParams):
    """Format the given range within a document"""
    logging.debug("%s", params)

    doc = ls.workspace.get_text_document(params.text_document.uri)
    rows = parse_document(doc, params.range)
    return format_table(rows, params.range)


@server.feature(
    types.TEXT_DOCUMENT_ON_TYPE_FORMATTING,
    types.DocumentOnTypeFormattingOptions(first_trigger_character="|"),
)
def format_on_type(ls: LanguageServer, params: types.DocumentOnTypeFormattingParams):
    """Format the document while the user is typing"""
    logging.debug("%s", params)

    doc = ls.workspace.get_text_document(params.text_document.uri)
    rows = parse_document(doc)
    return format_table(rows)


def format_table(
    rows: List[Row], range_: Optional[types.Range] = None
) -> List[types.TextEdit]:
    """Format the given table, returning the list of edits to make to the document.

    If range is given, this method will only modify the document within the specified
    range.
    """
    edits: List[types.TextEdit] = []

    # Determine max widths
    columns: Dict[int, int] = {}
    for row in rows:
        for idx, cell in enumerate(row.cells):
            columns[idx] = max(len(cell), columns.get(idx, 0))

    # Format the table.
    cell_padding = 2
    for row in rows:
        # Only process the lines within the specified range.
        if skip_line(row.line_number, range_):
            continue

        if len(row.cells) == 0:
            # If there are no cells on the row, then this must be a separator row
            cells: List[str] = []
            empty_cells = [
                "-" * (columns[i] + cell_padding) for i in range(len(columns))
            ]
        else:
            # Otherwise ensure that each row has a consistent number of cells
            empty_cells = [" " for _ in range(len(columns) - len(row.cells))]
            cells = [
                c.center(columns[i] + cell_padding) for i, c in enumerate(row.cells)
            ]

        line = f"|{'|'.join([*cells, *empty_cells])}|\n"
        edits.append(
            types.TextEdit(
                range=types.Range(
                    start=types.Position(line=row.line_number, character=0),
                    end=types.Position(line=row.line_number + 1, character=0),
                ),
                new_text=line,
            )
        )

    return edits


def parse_document(
    document: TextDocument, range_: Optional[types.Range] = None
) -> List[Row]:
    """Parse the given document into a list of table rows.

    If range_ is given, only consider lines within the range part of the table.
    """
    rows: List[Row] = []
    for linum, line in enumerate(document.lines):
        if skip_line(linum, range_):
            continue

        line = line.strip()
        cells = [c.strip() for c in line.split("|")]

        if line.startswith("|"):
            cells.pop(0)

        if line.endswith("|"):
            cells.pop(-1)

        chars = set()
        for c in cells:
            chars.update(set(c))

        logging.debug("%s: %s", chars, cells)

        if chars == {"-"}:
            # Check for a separator row, use an empty list to represent it.
            cells = []

        elif len(cells) == 0:
            continue

        row = Row(cells=cells, line_number=linum, cell_widths=[len(c) for c in cells])

        logging.debug("%s", row)
        rows.append(row)

    return rows


def skip_line(line: int, range_: Optional[types.Range]) -> bool:
    """Given a range, determine if we should skip the given line number."""

    if range_ is None:
        return False

    return any([line < range_.start.line, line > range_.end.line])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
