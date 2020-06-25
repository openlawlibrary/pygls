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

-- Language Features - Document Highlight --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Optional

from pygls.lsp.types.basic_structures import (PartialResultParams, Position, ProgressToken, Range,
                                              TextDocumentIdentifier, TextDocumentPositionParams,
                                              WorkDoneProgressOptions, WorkDoneProgressParams)


class DocumentHighlightClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentHighlightOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentHighlightParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        TextDocumentPositionParams.__init__(self, text_document, position)
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)


class DocumentHighlightKind(enum.IntEnum):
    Text = 1
    Read = 2
    Write = 3


class DocumentHighlight:
    def __init__(self,
                 range: Range,
                 kind: Optional[DocumentHighlightKind] = DocumentHighlightKind.Text):
        self.range = range
        self.kind = kind
