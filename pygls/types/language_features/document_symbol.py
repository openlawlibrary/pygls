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

-- Language Features - Document Symbol --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import List, Optional

from pygls.types.basic_structures import (Location, PartialResultParams, ProgressToken, Range,
                                          TextDocumentIdentifier, WorkDoneProgressOptions,
                                          WorkDoneProgressParams)


class DocumentSymbolClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 symbol_kind: Optional['WorkspaceCapabilitiesSymbolKind'] = None,
                 hierarchical_document_symbol_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration,
        self.symbolKind = symbol_kind
        self.hierarchicalDocumentSymbolSupport = hierarchical_document_symbol_support


class WorkspaceCapabilitiesSymbolKind:
    def __init__(self, value_set: Optional[List['SymbolKind']] = None):
        self.valueSet = value_set


class DocumentSymbolOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentSymbolParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)
        self.textDocument = text_document


class SymbolKind(enum.IntEnum):
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18
    Object = 19
    Key = 20
    Null = 21
    EnumMember = 22
    Struct = 23
    Event = 24
    Operator = 25
    TypeParameter = 26


class DocumentSymbol:
    def __init__(self,
                 name: str,
                 kind: SymbolKind,
                 range: Range,
                 selection_range: Range,
                 detail: Optional[str] = None,
                 children: Optional[List['DocumentSymbol']] = None,
                 deprecated: Optional[bool] = False):
        self.name = name
        self.kind = kind
        self.range = range
        self.selectionRange = selection_range
        self.detail = detail
        self.children = children
        self.deprecated = deprecated


class SymbolInformation:
    def __init__(self,
                 name: str,
                 kind: int,
                 location: Location,
                 container_name: Optional[str] = None,
                 deprecated: Optional[bool] = False):
        self.name = name
        self.kind = kind
        self.location = location
        self.containerName = container_name
        self.deprecated = deprecated