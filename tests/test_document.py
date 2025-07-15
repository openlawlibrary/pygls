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
from pygls.workspace import TextDocument, PositionCodec
import pytest
from .conftest import DOC, DOC_URI


def test_document_empty_edit():
    doc = TextDocument("file:///uri", "")
    change = types.TextDocumentContentChangePartial(
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

    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=2, character=0),
            end=types.Position(line=2, character=0),
        ),
        range_length=0,
        text="o",
    )
    doc.apply_change(change)

    assert list(doc.lines) == [
        "print 'a'\n",
        "print 'b'\n",
        "o",
    ]


def test_document_full_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Full
    )
    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert list(doc.lines) == ["print a, b"]

    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Full
    )
    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=0, character=0),
            end=types.Position(line=0, character=0),
        ),
        text="print a, b",
    )
    doc.apply_change(change)

    assert list(doc.lines) == ["print a, b"]


def test_document_line_edit():
    doc = TextDocument("file:///uri", "itshelloworld")
    change = types.TextDocumentContentChangePartial(
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
    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert list(doc.lines) == ["def hello(a, b):\n", "    print a, b\n"]

    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.Incremental
    )
    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        text="print a, b",
    )
    doc.apply_change(change)

    assert list(doc.lines) == ["def hello(a, b):\n", "    print a, b\n"]


def test_document_no_edit():
    old = ["def hello(a, b):\n", "    print a\n", "    print b\n"]
    doc = TextDocument(
        "file:///uri", "".join(old), sync_kind=types.TextDocumentSyncKind.None_
    )
    change = types.TextDocumentContentChangePartial(
        range=types.Range(
            start=types.Position(line=1, character=4),
            end=types.Position(line=2, character=11),
        ),
        range_length=0,
        text="print a, b",
    )
    doc.apply_change(change)

    assert list(doc.lines) == old


def test_document_props():
    doc = TextDocument(DOC_URI, DOC)

    assert doc.uri == DOC_URI
    assert doc.source == DOC


def test_document_source_unicode():
    document_mem = TextDocument(DOC_URI, "my source")
    document_disk = TextDocument(DOC_URI)
    assert isinstance(document_mem.source, type(document_disk.source))


SAMPLE_STRING = (
    "\u00e4"  # Non-ASCII character (latin small letter a with diaeresis) -- one utf-16 code units, 2 utf-8 code units
    "\u0061\u0308"  # Same letter but decomposed to "a" and combining diaeresis (NFD) -- 2 utf-16 code units, 3 utf-8 code units
    "錯誤"  # Characters in BMP but with 3-byte utf-8 encodings -- 2 utf-16 code units, 2x3 utf-8 code units
    "😋"  # Emoji (outside Basic Multilingual Plane) -- one codepoint, 2 utf-16 codepoints, 4 utf-8 codepoints
    "\n"  # To trigger offset calculation bugs in multiline documents
    # and all that again
    "\u00e4"
    "\u0061\u0308"
    "錯誤"
    "😋"
)

CODECS = (
    # use explicit little-endian encodings that don't emit a byte order mark
    (PositionCodec(encoding=types.PositionEncodingKind.Utf32), "utf-32-le", 4),
    (PositionCodec(encoding=types.PositionEncodingKind.Utf16), "utf-16-le", 2),
    (PositionCodec(encoding=types.PositionEncodingKind.Utf8), "utf-8", 1),
)


@pytest.mark.parametrize(
    ["position_codec", "codec_name", "code_unit_size"],
    CODECS,
)
def test_length_consistency(position_codec, codec_name, code_unit_size):
    # Test that the string codec and the position codec agree on how long the encoded string is
    assert (
        len(SAMPLE_STRING.encode(codec_name))
        == position_codec.client_num_units(SAMPLE_STRING) * code_unit_size
    )

    # and that they agree going through codepoint by codepoint as well (to avoid off-by-ones cancelling each other out)
    for end in range(len(SAMPLE_STRING) + 1):
        sliced = SAMPLE_STRING[:end]
        encoded = sliced.encode(codec_name)
        assert position_codec.client_num_units(sliced) * code_unit_size == len(encoded)


@pytest.mark.parametrize(
    ["position_codec", "codec_name", "code_unit_size"],
    CODECS,
)
def test_encoding_position_consistency(position_codec, codec_name, code_unit_size):
    encoded = SAMPLE_STRING.encode(codec_name)
    for column in range(len(SAMPLE_STRING)):
        utf32_pos = types.Position(line=0, character=column)
        client_pos = position_codec.position_to_client_units([SAMPLE_STRING], utf32_pos)
        # The position that we get from position_to_client_units
        # should be the right number of code units to cut off the
        # beginning in order to get back the same string. This
        # assertion ensures both that the codecs agree on the offsets,
        # and that we don't emit positions in the middle of a
        # multi-code-unit codepoint (since then the `decode` would fail).
        byte_pos = client_pos.character * code_unit_size
        assert encoded[byte_pos:].decode(codec_name) == SAMPLE_STRING[column:]

        # And the conversion should roundtrip.
        assert (
            position_codec.position_from_client_units([SAMPLE_STRING], client_pos)
            == utf32_pos
        )


def test_position_from_utf16():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=5)
    ) == types.Position(line=0, character=4)


def test_position_from_utf32():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf32)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=4)


def test_position_from_utf8():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf8)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)
    assert codec.position_from_client_units(
        ['x="😋"'], types.Position(line=0, character=7)
    ) == types.Position(line=0, character=4)


def test_position_to_utf16():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=5)


def test_position_to_utf32():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf32)
    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=4)


def test_position_to_utf8():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf8)
    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=3)
    ) == types.Position(line=0, character=3)

    assert codec.position_to_client_units(
        ['x="😋"'], types.Position(line=0, character=4)
    ) == types.Position(line=0, character=7)


def test_range_from_utf16():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    assert codec.range_from_client_units(
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
    actual = codec.range_from_client_units(['x="😋😋"'], range)
    expected = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=4),
    )
    assert actual == expected


def test_range_to_utf16():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    assert codec.range_to_client_units(
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
    actual = codec.range_to_client_units(['x="😋😋"'], range)
    expected = types.Range(
        start=types.Position(line=0, character=3),
        end=types.Position(line=0, character=5),
    )
    assert actual == expected


@pytest.mark.parametrize(
    ["position_codec", "codec_name", "code_unit_size"],
    CODECS,
)
def test_offset_at_position(position_codec, codec_name, code_unit_size):
    document = TextDocument(
        DOC_URI,
        SAMPLE_STRING,
        position_codec=position_codec,
    )
    # Test all existing positions in the document
    expected_offset = 0
    for line_index, line in enumerate(document.lines):
        for code_point_index, code_point in enumerate(line):
            # The encoded partial line is needed to calculate the number of code units in the respective encoding
            # The python encode method is assumed to be correct and therefore used as a reference
            partial_line_encoded = line[:code_point_index].encode(codec_name)
            client_position = types.Position(
                line=line_index, character=len(partial_line_encoded) // code_unit_size
            )
            offset = document.offset_at_position(client_position)
            assert document.source[offset] == code_point
            assert offset == expected_offset
            # When iterating over the code points of document.source,
            # the correct offset is always one more than in the previous iteration
            expected_offset += 1


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
    doc = TextDocument(
        DOC_URI,
        DOC,
        position_codec=PositionCodec(encoding=types.PositionEncodingKind.Utf32),
    )
    assert doc.offset_at_position(types.Position(line=0, character=8)) == 8
    assert doc.offset_at_position(types.Position(line=5, character=0)) == 39


def test_offset_at_position_utf8():
    doc = TextDocument(
        DOC_URI,
        DOC,
        position_codec=PositionCodec(encoding=types.PositionEncodingKind.Utf8),
    )
    assert doc.offset_at_position(types.Position(line=0, character=8)) == 8
    assert doc.offset_at_position(types.Position(line=5, character=0)) == 42


def test_utf16_to_utf32_position_cast():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    lines = ["", "😋😋", ""]
    assert codec.position_from_client_units(
        lines, types.Position(line=0, character=0)
    ) == types.Position(line=0, character=0)
    assert codec.position_from_client_units(
        lines, types.Position(line=0, character=1)
    ) == types.Position(line=0, character=0)
    assert codec.position_from_client_units(
        lines, types.Position(line=1, character=0)
    ) == types.Position(line=1, character=0)
    assert codec.position_from_client_units(
        lines, types.Position(line=1, character=2)
    ) == types.Position(line=1, character=1)
    assert codec.position_from_client_units(
        lines, types.Position(line=1, character=3)
    ) == types.Position(line=1, character=2)
    assert codec.position_from_client_units(
        lines, types.Position(line=1, character=4)
    ) == types.Position(line=1, character=2)
    assert codec.position_from_client_units(
        lines, types.Position(line=1, character=100)
    ) == types.Position(line=1, character=2)
    assert codec.position_from_client_units(
        lines, types.Position(line=3, character=0)
    ) == types.Position(line=2, character=0)
    assert codec.position_from_client_units(
        lines, types.Position(line=4, character=10)
    ) == types.Position(line=2, character=0)


def test_position_for_line_endings():
    codec = PositionCodec(encoding=types.PositionEncodingKind.Utf16)
    lines = ["x\r\n", "y\n"]
    assert codec.position_from_client_units(
        lines, types.Position(line=0, character=10)
    ) == types.Position(line=0, character=1)
    assert codec.position_from_client_units(
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
