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

-- Language Features - Completion --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Any, List, Optional, Union

from pygls.lsp.types.basic_structures import (Command, MarkupContent, MarkupKind, Model,
                                              PartialResultParams, TextDocumentPositionParams,
                                              TextEdit, WorkDoneProgressOptions,
                                              WorkDoneProgressParams)


class CompletionTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3


class CompletionContext(Model):
    trigger_kind: CompletionTriggerKind
    trigger_character: Optional[str] = None


class InsertTextFormat(enum.IntEnum):
    PlainText = 1
    Snippet = 2


class CompletionItemTag(enum.IntEnum):
    Deprecated = 1


class CompletionItemKind(enum.IntEnum):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class CompletionOptions(WorkDoneProgressOptions):
    trigger_characters: Optional[List[str]] = None
    all_commit_characters: Optional[List[str]] = None
    resolve_provider: Optional[bool] = False


class CompletionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    context: Optional['CompletionContext'] = None


class CompletionItemKindClientCapabilities(Model):
    value_set: Optional[List[CompletionItemKind]] = None


class CompletionTagSupportClientCapabilities(Model):
    value_set: Optional[List[CompletionItemTag]] = None


class CompletionItemClientCapabilities(Model):
    snippet_support: Optional[bool] = False
    commit_characters_support: Optional[bool] = False
    documentation_format: Optional[List[MarkupKind]] = None
    deprecated_support: Optional[bool] = False
    preselect_support: Optional[bool] = False
    tag_support: Optional[CompletionTagSupportClientCapabilities] = None


class CompletionClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    completion_item: Optional[CompletionItemClientCapabilities] = None
    completion_item_kind: Optional[CompletionItemKindClientCapabilities] = None
    context_support: Optional[bool] = False


class CompletionItem(Model):
    label: str
    kind: Optional[CompletionItemKind] = None
    tags: Optional[List[CompletionItemTag]] = None
    detail: Optional[str] = None
    documentation: Optional[Union[str, MarkupContent]] = None
    deprecated: Optional[bool] = False
    preselect: Optional[bool] = False
    sort_text: Optional[str] = None
    filter_text: Optional[str] = None
    insert_text: Optional[str] = None
    insert_text_format: Optional[InsertTextFormat] = None
    text_edit: Optional[TextEdit] = None
    additional_text_edits: Optional[List[TextEdit]] = None
    commit_characters: Optional[List[str]] = None
    command: Optional[Command] = None
    data: Optional[Any] = None


class CompletionList(Model):
    is_incomplete: bool
    items: List[CompletionItem] = []

    def add_item(self, completion_item):
        self.items.append(completion_item)

    def add_items(self, completion_items):
        self.items.extend(completion_items)
