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
from typing import Optional, Union, Sequence

from lsprotocol import types

log = logging.getLogger(__name__)


class UnitCounter:
    def code_units_for_char(self, char: str) -> int:
        """
        Get the number of code units used to encode the given single character.
        """
        raise NotImplementedError

    def num_units(self, chars: str) -> int:
        """
        Get the number of code units used to encode the given string.
        """
        return sum(self.code_units_for_char(c) for c in chars)

    def column_from_utf32(self, line: str, column: int) -> int:
        """
        Convert the codepoint index `column` into code units.
        """
        return sum(self.code_units_for_char(c) for c in line[:column])


class Utf32(UnitCounter):
    def code_units_for_char(self, char: str) -> int:
        return 1

    def num_units(self, chars: str) -> int:
        # We can avoid the loop needed for other encodings here
        return len(chars)

    def column_from_utf32(self, line: str, column: int) -> int:
        return column


def is_beyond_basic_multilingual_plane(char: str) -> bool:
    return ord(char) > 0xFFFF


class Utf16(UnitCounter):
    def code_units_for_char(self, char: str) -> int:
        if is_beyond_basic_multilingual_plane(char):
            return 2
        return 1


class Utf8(UnitCounter):
    def code_units_for_char(self, char: str) -> int:
        codepoint = ord(char)
        if codepoint < 0x80:
            return 1
        if codepoint < 0x800:
            return 2
        if codepoint < 0x10000:
            return 3
        return 4


impls: dict["str | types.PositionEncodingKind | None", UnitCounter] = {
    types.PositionEncodingKind.Utf8: Utf8(),
    types.PositionEncodingKind.Utf16: Utf16(),
    types.PositionEncodingKind.Utf32: Utf32(),
}


class PositionCodec:
    def __init__(
        self,
        encoding: Optional[
            Union[types.PositionEncodingKind, str]
        ] = types.PositionEncodingKind.Utf16,
    ):
        self.encoding = encoding
        self.impl = impls.get(encoding, Utf16())

    def __repr__(self):
        return f"<{self.__class__.__name__}, encoding {self.encoding}>"

    def client_num_units(self, string: str):
        return self.impl.num_units(string)

    def position_from_client_units(
        self, lines: Sequence[str], position: types.Position
    ) -> types.Position:
        """
        Convert the position.character from UTF-[32|16|8] code units to UTF-32.

        A python application can't use the character member of `Position`
        directly. As per specification it is represented as a zero-based line and
        character offset based on posible a UTF-[32|16|8] string representation.

        All characters whose code point exceeds the Basic Multilingual Plane are
        represented by 2 UTF-16 or 4 UTF-8 code units.

        The offset of the closing quotation mark in x="😋" is
        - 7 in UTF-8 representation
        - 5 in UTF-16 representation
        - 4 in UTF-32 representation

        see: https://github.com/microsoft/language-server-protocol/issues/376

        Arguments:
            lines (sequence):
                The content of the document which the position refers to.
            position (Position):
                The line and character offset in UTF-[32|16|8] code units.

        Returns:
            The position with `character` being converted to UTF-32 code units.
        """
        if len(lines) == 0:
            return types.Position(0, 0)
        if position.line >= len(lines):
            return types.Position(len(lines) - 1, self.impl.num_units(lines[-1]))

        _line = lines[position.line]
        _line = _line.replace("\r\n", "\n")  # TODO: it's a bit of a hack
        _client_len = self.impl.num_units(_line)

        if _client_len == 0:
            return types.Position(position.line, 0)

        if position.character > _client_len:
            position.character = _client_len - 1

        client_position = 0
        utf32_index = 0
        for c in _line:
            if client_position >= position.character:
                break
            client_position += self.impl.code_units_for_char(c)
            utf32_index += 1

        if client_position < position.character:
            utf32_index = len(_line)

        return types.Position(line=position.line, character=utf32_index)

    def position_to_client_units(
        self, lines: Sequence[str], position: types.Position
    ) -> types.Position:
        """
        Convert the position.character from its internal UTF-32 representation
        to client-supported UTF-[32|16|8] code units.

        Arguments:
            lines (sequence):
                The content of the document which the position refers to.
            position (Position):
                The line and character offset in UTF-32 code units.

        Returns:
            The position with `character` being converted to UTF-[32|16|8] code units.
        """
        try:
            character = self.impl.num_units(lines[position.line][: position.character])
            return types.Position(
                line=position.line,
                character=character,
            )
        except IndexError:
            return types.Position(line=len(lines), character=0)

    def range_from_client_units(
        self, lines: Sequence[str], range: types.Range
    ) -> types.Range:
        """
        Convert range.[start|end].character from UTF-[32|16|8] code units to UTF-32.

        Arguments:
            lines (sequence):
                The content of the document which the range refers to.
            range (Range):
                The line and character offset in UTF-[32|16|8] code units.

        Returns:
            The range with `character` offsets being converted to UTF-32 code units.
        """
        range_new = types.Range(
            start=self.position_from_client_units(lines, range.start),
            end=self.position_from_client_units(lines, range.end),
        )
        return range_new

    def range_to_client_units(
        self, lines: Sequence[str], range: types.Range
    ) -> types.Range:
        """
        Convert range.[start|end].character from UTF-32 to UTF-[32|16|8] code units.

        Arguments:
            lines (sequence):
                The content of the document which the range refers to.
            range (Range):
                The line and character offset in code points.

        Returns:
            The range with `character` offsets converted to UTF-[32|16|8] code units.
        """
        return types.Range(
            start=self.position_to_client_units(lines, range.start),
            end=self.position_to_client_units(lines, range.end),
        )
