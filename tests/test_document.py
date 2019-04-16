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
from pygls.types import (Position, Range, TextDocumentContentChangeEvent,
                         TextDocumentSyncKind)
from pygls.workspace import Document

from .conftest import DOC, DOC_URI


def test_document_empty_edit():
    doc = Document('file:///uri', u'')
    change = TextDocumentContentChangeEvent(
        Range(Position(0, 0), Position(0, 0)), 0, u'f')
    doc.apply_change(change)
    assert doc.source == u'f'


def test_document_end_of_file_edit():
    old = [
        "print 'a'\n",
        "print 'b'\n"
    ]
    doc = Document('file:///uri', u''.join(old))

    change = TextDocumentContentChangeEvent(
        Range(Position(2, 0), Position(2, 0)), 0, u'o')
    doc.apply_change(change)

    assert doc.lines == [
        "print 'a'\n",
        "print 'b'\n",
        "o",
    ]


def test_document_full_edit():
    old = [
        "def hello(a, b):\n",
        "    print a\n",
        "    print b\n"
    ]
    doc = Document('file:///uri', u''.join(old), sync_kind=TextDocumentSyncKind.FULL)
    change = TextDocumentContentChangeEvent(
        Range(Position(1, 4), Position(2, 11)), 0, u'print a, b')
    doc.apply_change(change)

    assert doc.lines == [
        "print a, b"
    ]


def test_document_line_edit():
    doc = Document('file:///uri', u'itshelloworld')
    change = TextDocumentContentChangeEvent(
        Range(Position(0, 3), Position(0, 8)), 0, u'goodbye')
    doc.apply_change(change)
    assert doc.source == u'itsgoodbyeworld'


def test_document_lines(doc):
    assert len(doc.lines) == 3
    assert doc.lines[0] == 'document\n'


def test_document_multiline_edit():
    old = [
        "def hello(a, b):\n",
        "    print a\n",
        "    print b\n"
    ]
    doc = Document('file:///uri', u''.join(old), sync_kind=TextDocumentSyncKind.INCREMENTAL)
    change = TextDocumentContentChangeEvent(
        Range(Position(1, 4), Position(2, 11)), 0, u'print a, b')
    doc.apply_change(change)

    assert doc.lines == [
        "def hello(a, b):\n",
        "    print a, b\n"
    ]


def test_document_no_edit():
    old = [
        "def hello(a, b):\n",
        "    print a\n",
        "    print b\n"
    ]
    doc = Document('file:///uri', u''.join(old), sync_kind=TextDocumentSyncKind.NONE)
    change = TextDocumentContentChangeEvent(
        Range(Position(1, 4), Position(2, 11)), 0, u'print a, b')
    doc.apply_change(change)

    assert doc.lines == old


def test_document_props(doc):
    assert doc.uri == DOC_URI
    assert doc.source == DOC


def test_document_source_unicode():
    document_mem = Document(DOC_URI, u'my source')
    document_disk = Document(DOC_URI)
    assert isinstance(document_mem.source, type(document_disk.source))


def test_offset_at_position(doc):
    assert doc.offset_at_position(Position(0, 8)) == 8
    assert doc.offset_at_position(Position(1, 5)) == 14
    assert doc.offset_at_position(Position(2, 0)) == 13
    assert doc.offset_at_position(Position(2, 4)) == 17
    assert doc.offset_at_position(Position(4, 0)) == 21


def test_word_at_position(doc):
    """
    Return the position under the cursor (or last in line if past the end)
    """
    assert doc.word_at_position(Position(0, 8)) == 'document'
    assert doc.word_at_position(Position(0, 1000)) == 'document'
    assert doc.word_at_position(Position(1, 5)) == 'for'
    assert doc.word_at_position(Position(2, 0)) == 'testing'
    assert doc.word_at_position(Position(4, 0)) == ''
