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
from pygls.lsp.types import Location, Position, Range


def test_position():
    assert Position(1, 2) == Position(1, 2)
    assert Position(1, 2) != Position(2, 2)
    assert Position(1, 2) <= Position(2, 2)
    assert Position(2, 2) >= Position(2, 0)
    assert Position(1, 2) != 'something else'
    assert "1:2" == repr(Position(1, 2))


def test_range():
    assert Range(Position(1, 2), Position(3, 4)) \
        == Range(Position(1, 2), Position(3, 4))
    assert Range(Position(0, 2), Position(3, 4)) \
        != Range(Position(1, 2), Position(3, 4))
    assert Range(Position(0, 2), Position(3, 4)) != 'something else'
    assert "1:2-3:4" == repr(Range(Position(1, 2), Position(3, 4)))


def test_location():
    assert Location(uri="file:///document.txt", range=Range(Position(1, 2), Position(3, 4))) \
        == Location(uri="file:///document.txt", range=Range(Position(1, 2), Position(3, 4)))
    assert Location(uri="file:///document.txt", range=Range(Position(1, 2), Position(3, 4))) \
        != Location(uri="file:///another.txt", range=Range(Position(1, 2), Position(3, 4)))
    assert Location(uri="file:///document.txt", range=Range(Position(1, 2), Position(3, 4))) \
        != 'something else'
    assert "file:///document.txt:1:2-3:4" == repr(Location(
        uri="file:///document.txt",
        range=Range(Position(1, 2), Position(3, 4))))
