############################################################################
# Original work Copyright 2018 Palantir Technologies, Inc.                 #
# Original work licensed under the MIT License.                            #
# See ThirdPartyNotices.txt in the project root for license information.   #
# All modifications Copyright (c) Open Law Library. All rights reserved.   #
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
import re

from lsprotocol import types
from pygls.workspace import TextDocument, Position
from .conftest import DOC, DOC_URI


def test_document_empty_edit():
    doc = TextDocument("file:///uri", "")
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=0, character=0),
            end=types.Position(line=0, character=0),
        ),
        range_length=0,
        text="f",
    )
    doc.apply_change(change)
    assert doc.source == "f"


def test_document_end_of_file_edit():
    old = ["print 'a'\n", "print 'b'\n"]
    doc = TextDocument("file:///uri", "".join(old))

    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=2, character=0),
            end=types.Position(line=2, character=0),
        ),
        range_length=0,
        text="o",
    )
    doc.apply_change(change)

    assert doc.lines == [
        "print 'a'\n",
        "print 'b'\n",
        "o",
    ]


def test_document_full_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Full
    )
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["print a, b"]

    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Full
    )
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=0, character=0),
            end=types.Position(line=0, character=0),
        ),
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["print a, b"]


def test_document_line_edit():
    doc = TextDocument("file:///uri", "itshelloworld")
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=0, character=3),
            end=types.Position(line=0, character=8),
        ),
        range_length=0,
        text="goodbye",
    )
    doc.apply_change(change)
    assert doc.source == "itsgoodbyeworld"


def test_document_lines():
    doc = TextDocument(DOC_URI, DOC)
    assert len(doc.lines) == 4
    assert doc.lines[0] == "document\n"


def test_document_multiline_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Incremental
    )
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["def hello(a, b):\n", "    print a, b\n"]

    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Incremental
    )
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["def hello(a, b):\n", "    print a, b\n"]


def test_document_no_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.None_
    )
    change = types.TextDocumentContentChangeEvent_Type1(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == old


def test_document_props():
    doc = TextDocument(DOC_URI, DOC)

    assert doc.uri == DOC_URI
    assert doc.source == DOC


def test_document_source_unicode():
    document_mem = TextDocument(DOC_URI, "my source")
    document_disk = TextDocument(DOC_URI)
    assert isinstance(document_mem.source, type(document_disk.source))


def test_position_from_utf16():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=5)
    ) == types.Position(line=0, character=4)


def test_position_from_utf32():
    position = Position(encoding=types.PositionEncodingKind.Utf32)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=4)


def test_position_from_utf8():
    position = Position(encoding=types.PositionEncodingKind.Utf8)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert position.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=7)
    ) == types.Position(line=0, character=4)


def test_position_to_utf16():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=5)


def test_position_to_utf32():
    position = Position(encoding=types.PositionEncodingKind.Utf32)
    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=4)


def test_position_to_utf8():
    position = Position(encoding=types.PositionEncodingKind.Utf8)
    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert position.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=6)


def test_range_from_utf16():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    assert position.range_from_client_units(
        ['x="😋"'],
        types.Range(
            start=types.Position(line=0, character=3),
            end=types.Position(line=0, character=5),
        ),
    ) == types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=4),
    )

    range = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=5),
    )
    actual = position.range_from_client_units(['x="😋😋"'], range)
    expected = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=4),
    )
    assert actual == expected


def test_range_to_utf16():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    assert position.range_to_client_units(
        ['x="😋"'],
        types.Range(
            start=types.Position(line=0, character=3),
            end=types.Position(line=0, character=4),
        ),
    ) == types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=5),
    )

    range = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=4),
    )
    actual = position.range_to_client_units(['x="😋😋"'], range)
    expected = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=5),
    )
    assert actual == expected


def test_offset_at_position_utf16():
    doc = TextDocument(DOC_URI, DOC)
    assert doc.offset_at_position(types.Position(line=0, character=8)) == 8
    assert doc.offset_at_position(types.Position(line=1, character=5)) == 12
    assert doc.offset_at_position(types.Position(line=2, character=0)) == 13
    assert doc.offset_at_position(types.Position(line=2, character=4)) == 17
    assert doc.offset_at_position(types.Position(line=3, character=6)) == 27
    assert doc.offset_at_position(types.Position(line=3, character=7)) == 28
    assert doc.offset_at_position(types.Position(line=3, character=8)) == 28
    assert doc.offset_at_position(types.Position(line=4, character=0)) == 40
    assert doc.offset_at_position(types.Position(line=5, character=0)) == 40


def test_offset_at_position_utf32():
    doc = TextDocument(DOC_URI, DOC, position_encoding=types.PositionEncodingKind.Utf32)
    assert doc.offset_at_position(types.Position(line=0, character=8)) == 8
    assert doc.offset_at_position(types.Position(line=5, character=0)) == 39


def test_offset_at_position_utf8():
    doc = TextDocument(DOC_URI, DOC, position_encoding=types.PositionEncodingKind.Utf8)
    assert doc.offset_at_position(types.Position(line=0, character=8)) == 8
    assert doc.offset_at_position(types.Position(line=5, character=0)) == 41


def test_utf16_to_utf32_position_cast():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    lines = ["", "😋😋", ""]
    assert position.position_from_client_units(
        lines, types.Position(line=0, character=0)
    ) == types.Position(line=0, character=0)
    assert position.position_from_client_units(
        lines, types.Position(line=0, character=1)
    ) == types.Position(line=0, character=0)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=0)
    ) == types.Position(line=1, character=0)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=2)
    ) == types.Position(line=1, character=1)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=3)
    ) == types.Position(line=1, character=2)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=4)
    ) == types.Position(line=1, character=2)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=100)
    ) == types.Position(line=1, character=2)
    assert position.position_from_client_units(
        lines, types.Position(line=3, character=0)
    ) == types.Position(line=2, character=0)
    assert position.position_from_client_units(
        lines, types.Position(line=4, character=10)
    ) == types.Position(line=2, character=0)


def test_position_for_line_endings():
    position = Position(encoding=types.PositionEncodingKind.Utf16)
    lines = ["x\r\n", "y\n"]
    assert position.position_from_client_units(
        lines, types.Position(line=0, character=10)
    ) == types.Position(line=0, character=1)
    assert position.position_from_client_units(
        lines, types.Position(line=1, character=10)
    ) == types.Position(line=1, character=1)


def test_word_at_position():
    """
    Return word under the cursor (or last in line if past the end)
    """
    doc = TextDocument(DOC_URI, DOC)

    assert doc.word_at_position(types.Position(line=0, character=8)) == "document"
    assert doc.word_at_position(types.Position(line=0, character=1000)) == "document"
    assert doc.word_at_position(types.Position(line=1, character=5)) == "for"
    assert doc.word_at_position(types.Position(line=2, character=0)) == "testing"
    assert doc.word_at_position(types.Position(line=3, character=10)) == "unicode"
    assert doc.word_at_position(types.Position(line=4, character=0)) == ""
    assert doc.word_at_position(types.Position(line=4, character=0)) == ""
    re_start_word = re.compile(r"[A-Za-z_0-9.]*$")
    re_end_word = re.compile(r"^[A-Za-z_0-9.]*")
    assert (
        doc.word_at_position(
            types.Position(
                line=3,
                character=10,
            ),
            re_start_word=re_start_word,
            re_end_word=re_end_word,
        )
        == "unicode."
    )
