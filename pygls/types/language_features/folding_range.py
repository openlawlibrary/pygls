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

-- Language Features - Folding Range --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Any, List, Optional, Tuple, Union

from pygls.types.basic_structures import (DocumentSelector, MarkupContent, MarkupKind, NumType,
                                          PartialResultParams, Position, ProgressToken, Range,
                                          StaticRegistrationOptions, TextDocumentIdentifier,
                                          TextDocumentPositionParams,
                                          TextDocumentRegistrationOptions, TextEdit,
                                          WorkDoneProgressOptions, WorkDoneProgressParams)


class FoldingRangeClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 range_limit: Optional[NumType] = None,
                 line_folding_only: Optional[bool] = False,):
        self.dynamicRegistration = dynamic_registration
        self.rangeLimit = range_limit
        self.lineFoldingOnly = line_folding_only


class FoldingRangeOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class FoldingRangeRegistrationOptions(FoldingRangeOptions,
                                      TextDocumentRegistrationOptions,
                                      StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelector] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        FoldingRangeOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class FoldingRangeParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self, query: str,
                 text_document: TextDocumentIdentifier,
                 work_done_progress: Optional[ProgressToken] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(work_done_progress)
        PartialResultParams.__init__(partial_result_token)
        self.textDocument = text_document


class FoldingRangeKind(str, enum.Enum):
    Comment = 'comment'
    Imports = 'imports'
    Region = 'region'


class FoldingRange:
    def __init__(self,
                 start_line: int,
                 end_line: int,
                 start_character: Optional[int] = None,
                 end_character: Optional[int] = None,
                 kind: Optional[FoldingRangeKind] = None):
        self.startLine = start_line
        self.startCharacter = start_character
        self.endLine = end_line
        self.endCharacter = end_character
        self.kind = kind
