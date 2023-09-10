############################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.                 #
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
import logging
from typing import List

from lsprotocol.types import (
    Position,
    Range,
)


log = logging.getLogger(__name__)


def is_char_beyond_multilingual_plane(char: str) -> bool:
    return ord(char) > 0xFFFF


def utf16_unit_offset(chars: str):
    """
    Calculate the number of characters which need two utf-16 code units.

    Arguments:
        chars (str): The string to count occurrences of utf-16 code units for.
    """
    return sum(is_char_beyond_multilingual_plane(ch) for ch in chars)


def utf16_num_units(chars: str):
    """
    Calculate the length of `str` in utf-16 code units.

    Arguments:
        chars (str): The string to return the length in utf-16 code units for.
    """
    return len(chars) + utf16_unit_offset(chars)


def position_from_utf16(lines: List[str], position: Position) -> Position:
    """
    Convert the position.character from utf-16 code units to utf-32.

    A python application can't use the character member of `Position`
    directly. As per specification it is represented as a zero-based line and
    character offset based on a UTF-16 string representation.

    All characters whose code point exceeds the Basic Multilingual Plane are
    represented by 2 UTF-16 code units.

    The offset of the closing quotation mark in x="😋" is
    - 5 in UTF-16 representation
    - 4 in UTF-32 representation

    see: https://github.com/microsoft/language-server-protocol/issues/376

    Arguments:
        lines (list):
            The content of the document which the position refers to.
        position (Position):
            The line and character offset in utf-16 code units.

    Returns:
        The position with `character` being converted to utf-32 code units.
    """
    if len(lines) == 0:
        return Position(0, 0)
    if position.line >= len(lines):
        return Position(len(lines) - 1, utf16_num_units(lines[-1]))

    _line = lines[position.line]
    _line = _line.replace("\r\n", "\n")  # TODO: it's a bit of a hack
    _utf16_len = utf16_num_units(_line)
    _utf32_len = len(_line)

    if _utf16_len == 0:
        return Position(position.line, 0)

    _utf16_end_of_line = utf16_num_units(_line)
    if position.character > _utf16_end_of_line:
        position.character = _utf16_end_of_line - 1

    _utf16_index = 0
    utf32_index = 0
    while True:
        _is_searching_queried_position = _utf16_index < position.character
        _is_before_end_of_line = utf32_index < _utf32_len
        _is_searching_for_position = (
            _is_searching_queried_position and _is_before_end_of_line
        )
        if not _is_searching_for_position:
            break

        _current_char = _line[utf32_index]
        _is_double_width = is_char_beyond_multilingual_plane(_current_char)
        if _is_double_width:
            _utf16_index += 2
        else:
            _utf16_index += 1
        utf32_index += 1

    position = Position(line=position.line, character=utf32_index)
    return position


def position_to_utf16(lines: List[str], position: Position) -> Position:
    """
    Convert the position.character from utf-32 to utf-16 code units.

    A python application can't use the character member of `Position`
    directly as per specification it is represented as a zero-based line and
    character offset based on a UTF-16 string representation.

    All characters whose code point exceeds the Basic Multilingual Plane are
    represented by 2 UTF-16 code units.

    The offset of the closing quotation mark in x="😋" is
    - 5 in UTF-16 representation
    - 4 in UTF-32 representation

    see: https://github.com/microsoft/language-server-protocol/issues/376

    Arguments:
        lines (list):
            The content of the document which the position refers to.
        position (Position):
            The line and character offset in utf-32 code units.

    Returns:
        The position with `character` being converted to utf-16 code units.
    """
    try:
        return Position(
            line=position.line,
            character=position.character
            + utf16_unit_offset(lines[position.line][: position.character]),
        )
    except IndexError:
        return Position(line=len(lines), character=0)


def range_from_utf16(lines: List[str], range: Range) -> Range:
    """
    Convert range.[start|end].character from utf-16 code units to utf-32.

    Arguments:
        lines (list):
            The content of the document which the range refers to.
        range (Range):
            The line and character offset in utf-32 code units.

    Returns:
        The range with `character` offsets being converted to utf-16 code units.
    """
    range_new = Range(
        start=position_from_utf16(lines, range.start),
        end=position_from_utf16(lines, range.end),
    )
    return range_new


def range_to_utf16(lines: List[str], range: Range) -> Range:
    """
    Convert range.[start|end].character from utf-32 to utf-16 code units.

    Arguments:
        lines (list):
            The content of the document which the range refers to.
        range (Range):
            The line and character offset in utf-16 code units.

    Returns:
        The range with `character` offsets being converted to utf-32 code units.
    """
    return Range(
        start=position_to_utf16(lines, range.start),
        end=position_to_utf16(lines, range.end),
    )
