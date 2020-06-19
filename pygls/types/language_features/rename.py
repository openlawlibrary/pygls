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

-- Language Features - Rename --

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


class RenameClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 prepare_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.prepareSupport = prepare_support


class RenameOptions(WorkDoneProgressOptions):
    def __init__(self,
                 prepare_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.prepareProvider = prepare_provider


class RenameParams(TextDocumentPositionParams, WorkDoneProgressParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 new_name: str,
                 work_done_token: Optional[bool] = None):
        TextDocumentPositionParams.__init__(self, text_document, position)
        WorkDoneProgressParams.__init__(self, work_done_token)
        self.newName = new_name
