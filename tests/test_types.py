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
from lsprotocol.types import Location, Position, Range


def test_position():
    assert Position(line=1, character=2) == Position(line=1, character=2)
    assert Position(line=1, character=2) != Position(line=2, character=2)
    assert Position(line=1, character=2) <= Position(line=2, character=2)
    assert Position(line=2, character=2) >= Position(line=2, character=0)
    assert Position(line=1, character=2) != "something else"
    assert "1:2" == repr(Position(line=1, character=2))


def test_range():
    assert Range(
        start=Position(line=1, character=2), end=Position(line=3, character=4)
    ) == Range(
        start=Position(line=1, character=2), end=Position(line=3, character=4)
    )
    assert Range(
        start=Position(line=0, character=2), end=Position(line=3, character=4)
    ) != Range(
        start=Position(line=1, character=2), end=Position(line=3, character=4)
    )
    assert (
        Range(start=Position(line=0, character=2),
              end=Position(line=3, character=4))
        != "something else"
    )
    assert "1:2-3:4" == repr(
        Range(start=Position(line=1, character=2),
              end=Position(line=3, character=4))
    )


def test_location():
    assert Location(
        uri="file:///document.txt",
        range=Range(
            start=Position(line=1, character=2),
            end=Position(line=3, character=4)
        ),
    ) == Location(
        uri="file:///document.txt",
        range=Range(
            start=Position(line=1, character=2),
            end=Position(line=3, character=4)
        ),
    )
    assert Location(
        uri="file:///document.txt",
        range=Range(
            start=Position(line=1, character=2),
            end=Position(line=3, character=4)
        ),
    ) != Location(
        uri="file:///another.txt",
        range=Range(
            start=Position(line=1, character=2),
            end=Position(line=3, character=4)
        ),
    )
    assert (
        Location(
            uri="file:///document.txt",
            range=Range(
                start=Position(line=1, character=2),
                end=Position(line=3, character=4)
            ),
        )
        != "something else"
    )
    assert "file:///document.txt:1:2-3:4" == repr(
        Location(
            uri="file:///document.txt",
            range=Range(
                start=Position(line=1, character=2),
                end=Position(line=3, character=4)
            ),
        )
    )
