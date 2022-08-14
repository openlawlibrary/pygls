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

from lsprotocol.types import (
    Position,
    Range,
    TextDocumentContentChangeEvent_Type1,
    TextDocumentSyncKind,
)
from pygls.workspace import (
    Document,
    position_from_utf16,
    position_to_utf16,
    range_from_utf16,
    range_to_utf16,
)
from .conftest import DOC, DOC_URI


def test_document_empty_edit():
    doc = Document("file:///uri", "")
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=0, character=0),
            end=Position(line=0, character=0)
        ),
        range_length=0,
        text="f",
    )
    doc.apply_change(change)
    assert doc.source == "f"


def test_document_end_of_file_edit():
    old = ["print 'a'\n", "print 'b'\n"]
    doc = Document("file:///uri", "".join(old))

    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=2, character=0),
            end=Position(line=2, character=0)
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
    doc = Document("file:///uri", "".join(old),
                   sync_kind=TextDocumentSyncKind.Full)
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=1, character=4),
            end=Position(line=2, character=11)
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["print a, b"]

    doc = Document("file:///uri", "".join(old),
                   sync_kind=TextDocumentSyncKind.Full)
    change = TextDocumentContentChangeEvent_Type1(range=None, text="print a, b")
    doc.apply_change(change)

    assert doc.lines == ["print a, b"]


def test_document_line_edit():
    doc = Document("file:///uri", "itshelloworld")
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=0, character=3),
            end=Position(line=0, character=8)
        ),
        range_length=0,
        text="goodbye",
    )
    doc.apply_change(change)
    assert doc.source == "itsgoodbyeworld"


def test_document_lines(doc):
    assert len(doc.lines) == 4
    assert doc.lines[0] == "document\n"


def test_document_multiline_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = Document(
        "file:///uri", "".join(old), sync_kind=TextDocumentSyncKind.Incremental
    )
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=1, character=4),
            end=Position(line=2, character=11)
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["def hello(a, b):\n", "    print a, b\n"]

    doc = Document(
        "file:///uri", "".join(old), sync_kind=TextDocumentSyncKind.Incremental
    )
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=1, character=4),
            end=Position(line=2, character=11)
        ),
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == ["def hello(a, b):\n", "    print a, b\n"]


def test_document_no_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = Document("file:///uri", "".join(old),
                   sync_kind=TextDocumentSyncKind.None_)
    change = TextDocumentContentChangeEvent_Type1(
        range=Range(
            start=Position(line=1, character=4),
            end=Position(line=2, character=11)
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert doc.lines == old


def test_document_props(doc):
    assert doc.uri == DOC_URI
    assert doc.source == DOC


def test_document_source_unicode():
    document_mem = Document(DOC_URI, "my source")
    document_disk = Document(DOC_URI)
    assert isinstance(document_mem.source, type(document_disk.source))


def test_position_from_utf16():
    assert position_from_utf16(
        ['x="😋"'], Position(line=0, character=3)
    ) == Position(
        line=0, character=3
    )
    assert position_from_utf16(
        ['x="😋"'], Position(line=0, character=5)
    ) == Position(
        line=0, character=4
    )

    position = Position(line=0, character=5)
    position_from_utf16(['x="😋"'], position)
    assert position == Position(line=0, character=5)


def test_position_to_utf16():
    assert position_to_utf16(
        ['x="😋"'], Position(line=0, character=3)
    ) == Position(
        line=0, character=3
    )

    assert position_to_utf16(
        ['x="😋"'], Position(line=0, character=4)
    ) == Position(
        line=0, character=5
    )

    position = Position(line=0, character=4)
    position_to_utf16(['x="😋"'], position)
    assert position == Position(line=0, character=4)


def test_range_from_utf16():
    assert range_from_utf16(
        ['x="😋"'],
        Range(start=Position(line=0, character=3),
              end=Position(line=0, character=5)),
    ) == Range(
        start=Position(line=0, character=3),
        end=Position(line=0, character=4)
    )

    range = Range(
        start=Position(line=0, character=3), end=Position(line=0, character=5)
    )
    range_from_utf16(['x="😋"'], range)
    assert range == Range(
        start=Position(line=0, character=3), end=Position(line=0, character=5)
    )


def test_range_to_utf16():
    assert range_to_utf16(
        ['x="😋"'],
        Range(start=Position(line=0, character=3),
              end=Position(line=0, character=4)),
    ) == Range(
        start=Position(line=0, character=3),
        end=Position(line=0, character=5)
    )

    range = Range(
        start=Position(line=0, character=3), end=Position(line=0, character=4)
    )
    range_to_utf16(['x="😋"'], range)
    assert range == Range(
        start=Position(line=0, character=3), end=Position(line=0, character=4)
    )


def test_offset_at_position(doc):
    assert doc.offset_at_position(Position(line=0, character=8)) == 8
    assert doc.offset_at_position(Position(line=1, character=5)) == 14
    assert doc.offset_at_position(Position(line=2, character=0)) == 13
    assert doc.offset_at_position(Position(line=2, character=4)) == 17
    assert doc.offset_at_position(Position(line=3, character=6)) == 27
    assert doc.offset_at_position(Position(line=3, character=7)) == 27
    assert doc.offset_at_position(Position(line=3, character=8)) == 28
    assert doc.offset_at_position(Position(line=4, character=0)) == 39
    assert doc.offset_at_position(Position(line=5, character=0)) == 39


def test_word_at_position(doc):
    """
    Return word under the cursor (or last in line if past the end)
    """
    assert doc.word_at_position(Position(line=0, character=8)) == "document"
    assert doc.word_at_position(Position(line=0, character=1000)) == "document"
    assert doc.word_at_position(Position(line=1, character=5)) == "for"
    assert doc.word_at_position(Position(line=2, character=0)) == "testing"
    assert doc.word_at_position(Position(line=3, character=10)) == "unicode"
    assert doc.word_at_position(Position(line=4, character=0)) == ""
    assert doc.word_at_position(Position(line=4, character=0)) == ""
    re_start_word = re.compile(r"[A-Za-z_0-9.]*$")
    re_end_word = re.compile(r"^[A-Za-z_0-9.]*")
    assert (
        doc.word_at_position(
            Position(
                line=3,
                character=10,
            ),
            re_start_word=re_start_word,
            re_end_word=re_end_word,
        )
        == "unicode."
    )
