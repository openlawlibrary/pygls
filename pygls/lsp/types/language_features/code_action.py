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

-- Language Features - Code Action --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import List, Optional

from pygls.lsp.types.basic_structures import (Command, Diagnostic, PartialResultParams,
                                              ProgressToken, Range, TextDocumentIdentifier,
                                              WorkDoneProgressOptions, WorkDoneProgressParams,
                                              WorkspaceEdit)
from pygls.lsp.types.language_features.document_symbol import SymbolKind


class CodeActionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 code_action_literal_support: Optional['CodeActionLiteralSupportClientCapabilities'] = None,
                 is_preferred_support: Optional[bool] = False,):
        self.dynamicRegistration = dynamic_registration
        self.codeActionLiteralSupport = code_action_literal_support
        self.isPreferredSupport = is_preferred_support


class CodeActionLiteralSupportClientCapabilities:
    def __init__(self,
                 code_action_kind: Optional['CodeActionLiteralSupportActionKindClientCapabilities'] = None):
        self.codeActionKind = code_action_kind


class CodeActionLiteralSupportActionKindClientCapabilities:
    def __init__(self, value_set: Optional[List[SymbolKind]] = None):
        self.valueSet = value_set


class CodeActionOptions(WorkDoneProgressOptions):
    def __init__(self,
                 code_action_kinds: Optional[List['CodeActionKind']] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.codeActionKinds = code_action_kinds


class CodeActionParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 range: Range,
                 context: 'CodeActionContext',
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)
        self.textDocument = text_document
        self.range = range
        self.context = context


class CodeActionKind(str, enum.Enum):
    Empty = ''
    QuickFix = 'quickfix'
    Refactor = 'refactor'
    RefactorExtract = 'refactor.extract'
    RefactorInline = 'refactor.inline'
    RefactorRewrite = 'refactor.rewrite'
    Source = 'source'
    SourceOrganizeImports = 'source.organizeImports'


class CodeActionContext:
    def __init__(self,
                 diagnostics: List[Diagnostic],
                 only: Optional[List[CodeActionKind]] = None):
        self.diagnostics = diagnostics
        self.only = only


class CodeAction:
    def __init__(self,
                 title: str,
                 kind: Optional[CodeActionKind] = None,
                 diagnostics: Optional[List[Diagnostic]] = None,
                 is_preferred: Optional[bool] = None,
                 edit: Optional[WorkspaceEdit] = None,
                 command: Optional[Command] = None):
        self.title = title
        self.kind = kind
        self.diagnostics = diagnostics
        self.isPreferred = is_preferred
        self.edit = edit
        self.command = command
