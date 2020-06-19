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

-- Language Features - Formatting --

Class attributes are named with camel-case notation because client is expecting
that.
"""
from typing import Optional

from pygls.types.basic_structures import (
    ProgressToken,
    TextDocumentIdentifier,
    WorkDoneProgressOptions,
    WorkDoneProgressParams
)


class DocumentFormattingClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentFormattingOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentFormattingParams(WorkDoneProgressParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 options: 'FormattingOptions',
                 work_done_token: Optional[bool] = None):
        WorkDoneProgressParams.__init__(self, work_done_token)
        self.textDocument = text_document
        self.options = options


class FormattingOptions:
    def __init__(self,
                 tab_size: int,
                 insert_spaces: bool,
                 trim_trailing_whitespace: Optional[bool] = False,
                 insert_final_newline: Optional[bool] = False,
                 trim_final_newlines: Optional[bool] = False,
                 **kwargs):
        self.tabSize = tab_size
        self.insertSpaces = insert_spaces
        self.trimTrailingWhitespace = trim_trailing_whitespace
        self.insertFinalNewline = insert_final_newline
        self.trimFinalNewlines = trim_final_newlines
        self.kwargs = kwargs
