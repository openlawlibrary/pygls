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

-- Language Features - Document Link --

Class attributes are named with camel-case notation because client is expecting
that.
"""
from typing import Any, Optional

from pygls.types.basic_structures import (
    PartialResultParams,
    ProgressToken,
    Range,
    TextDocumentIdentifier,
    WorkDoneProgressOptions,
    WorkDoneProgressParams
)


class DocumentLinkClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 tooltip_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.tooltipSupport = tooltip_support


class DocumentLinkOptions(WorkDoneProgressOptions):
    def __init__(self,
                 resolve_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.resolveProvider = resolve_provider


class DocumentLinkParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)
        self.textDocument = text_document


class DocumentLink:
    def __init__(self,
                 range: Range,
                 target: Optional[str] = None,
                 tooltip: Optional[str] = None,
                 data: Optional[Any] = None):
        self.range = range
        self.target = target
        self.tooltip = tooltip
        self.data = data
