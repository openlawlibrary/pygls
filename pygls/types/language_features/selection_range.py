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

-- Language Features - Selection Range --

Class attributes are named with camel-case notation because client is expecting
that.
"""
from typing import List, Optional

from pygls.types.basic_structures import (DocumentSelector, PartialResultParams, Position,
                                          ProgressToken, Range, StaticRegistrationOptions,
                                          TextDocumentIdentifier, TextDocumentRegistrationOptions,
                                          WorkDoneProgressOptions, WorkDoneProgressParams)


class SelectionRangeClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class SelectionRangeOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class SelectionRangeRegistrationOptions(SelectionRangeOptions,
                                        TextDocumentRegistrationOptions,
                                        StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelector] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        SelectionRangeOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class SelectionRangeParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self, query: str,
                 text_document: TextDocumentIdentifier,
                 positions: List[Position],
                 work_done_progress: Optional[ProgressToken] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(work_done_progress)
        PartialResultParams.__init__(partial_result_token)
        self.textDocument = text_document
        self.positions = positions


class SelectionRange:
    def __init__(self, range: Range, parent: Optional['SelectionRange'] = None):
        self.range = range
        self.parent = parent
