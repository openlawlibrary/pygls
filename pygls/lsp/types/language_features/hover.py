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

-- Language Features - Hover --

Class attributes are named with camel-case notation because client is expecting
that.
"""
from typing import List, Optional, Union

from pygls.lsp.types.basic_structures import (MarkupContent, MarkupKind, Position, ProgressToken,
                                              Range, TextDocumentIdentifier,
                                              TextDocumentPositionParams, WorkDoneProgressOptions,
                                              WorkDoneProgressParams)


class HoverClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 content_format: Optional[List[MarkupKind]] = None):
        self.dynamicRegistration = dynamic_registration
        self.contentFormat = content_format


class HoverOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class HoverParams(TextDocumentPositionParams, WorkDoneProgressParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 work_done_token: Optional[bool] = None):
        TextDocumentPositionParams.__init__(self, text_document, position)
        WorkDoneProgressParams.__init__(self, work_done_token)


class Hover:
    def __init__(self,
                 contents: Union['MarkedString', List['MarkedString'], MarkupContent],
                 range: Optional[Range] = None):
        self.contents = contents
        self.range = range


class _MarkedString:
    def __init__(self, language: str, value: str):
        self.language = language
        self.value = value


MarkedString = Union[str, _MarkedString]
