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

-- Language Features - Color Presentation --

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
from pygls.types.language_features.document_color import Color


class ColorPresentationParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 color: Color,
                 range: Range,
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)
        self.textDocument = text_document
        self.color = color
        self.range = range


class ColorPresentation:
    def __init__(self,
                 label: str,
                 text_edit: Optional[TextEdit] = None,
                 additional_text_edits: Optional[List[TextEdit]] = None):
        self.label = label
        self.textEdit = text_edit
        self.additionalTextEdits = additional_text_edits
