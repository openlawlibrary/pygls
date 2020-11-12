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
from typing import List, Optional, Union

from pygls.lsp.types.basic_structures import (Command, Diagnostic, Model, PartialResultParams,
                                              Range, TextDocumentIdentifier,
                                              TextDocumentRegistrationOptions,
                                              WorkDoneProgressOptions, WorkDoneProgressParams,
                                              WorkspaceEdit)


class CodeActionKind(str, enum.Enum):
    Empty = ''
    QuickFix = 'quickfix'
    Refactor = 'refactor'
    RefactorExtract = 'refactor.extract'
    RefactorInline = 'refactor.inline'
    RefactorRewrite = 'refactor.rewrite'
    Source = 'source'
    SourceOrganizeImports = 'source.organizeImports'


class CodeActionLiteralSupportActionKindClientCapabilities(Model):
    value_set: Optional[List[Union[str, CodeActionKind]]] = None


class CodeActionLiteralSupportClientCapabilities(Model):
    code_action_kind: Optional[CodeActionLiteralSupportActionKindClientCapabilities] = None


class CodeActionClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    code_action_literal_support: Optional[CodeActionLiteralSupportClientCapabilities] = None
    is_preferred_support: Optional[bool] = False


class CodeActionOptions(WorkDoneProgressOptions):
    code_action_kinds: Optional[List[CodeActionKind]] = None


class CodeActionRegistrationOptions(TextDocumentRegistrationOptions, CodeActionOptions):
    pass


class CodeActionContext(Model):
    diagnostics: List[Diagnostic]
    only: Optional[List[CodeActionKind]] = None


class CodeActionParams(WorkDoneProgressParams, PartialResultParams):
    text_document: TextDocumentIdentifier
    range: Range
    context: CodeActionContext


class CodeAction(Model):
    title: str
    kind: Optional[CodeActionKind] = None
    diagnostics: Optional[List[Diagnostic]] = None
    is_preferred: Optional[bool] = None
    edit: Optional[WorkspaceEdit] = None
    command: Optional[Command] = None
