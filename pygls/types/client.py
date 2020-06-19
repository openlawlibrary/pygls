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

-- Client --

Class attributes are named with camel-case notation because client is expecting
that.
"""
from typing import Any, List, Optional, Union


class Registration:
    def __init__(self, id: str, method: str, register_options: Optional[Any] = None):
        self.id = id
        self.method = method
        self.registerOptions = register_options


class RegistrationParams:
    def __init__(self, registrations: List[Registration]):
        self.registrations = registrations


class Unregistration:
    def __init__(self, id: str, method: str):
        self.id = id
        self.method = method


class UnregistrationParams:
    def __init__(self, unregisterations: List[Unregistration]):
        self.unregisterations = unregisterations
