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

-- Language Features - On Type Formatting --

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
from pygls.types.language_features.formatting import FormattingOptions


class DocumentOnTypeFormattingClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentOnTypeFormattingOptions(WorkDoneProgressOptions):
    def __init__(self,
                 first_trigger_character: str,
                 more_trigger_character: Optional[List[str]] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_character


class DocumentOnTypeFormattingParams(TextDocumentPositionParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 ch: str,
                 options: FormattingOptions):
        TextDocumentPositionParams.__init__(self, text_document, position)
        self.ch = ch
        self.options = options
