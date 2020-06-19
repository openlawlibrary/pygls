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
"""This module contains Language Server Protocol types
https://microsoft.github.io/language-server-protocol/specification

-- Window --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import List, Optional

from pygls.types.basic_structures import NumType, ProgressToken


class ShowMessageParams:
    def __init__(self, type: 'MessageType', message: str):
        self.type = type
        self.message = message


class MessageType(enum.IntEnum):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class ShowMessageRequestParams:
    def __init__(self,
                 type: MessageType,
                 message: str,
                 actions: Optional[List['MessageActionItem']] = None):
        self.type = type
        self.message = message
        self.actions = actions


class MessageActionItem:
    def __init__(self, title: str):
        self.title = title


class LogMessageParams:
    def __init__(self, type: NumType, message: str):
        self.type = type
        self.message = message


class WorkDoneProgressCreateParams:
    def __init__(self, token: ProgressToken):
        self.token = token


class WorkDoneProgressCancelParams:
    def __init__(self, token: ProgressToken):
        self.token = token
