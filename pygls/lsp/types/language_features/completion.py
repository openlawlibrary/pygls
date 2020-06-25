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

from pygls.lsp.types.basic_structures import (Command, MarkupContent, MarkupKind,
                                              PartialResultParams, Position, ProgressToken,
                                              TextDocumentIdentifier, TextDocumentPositionParams,
                                              TextEdit, WorkDoneProgressOptions,
                                              WorkDoneProgressParams)


class CompletionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 completion_item: Optional['CompletionItemClientCapabilities'] = None,
                 completion_item_kind: Optional['CompletionItemKindClientCapabilities'] = None,
                 context_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.completionItem = completion_item
        self.completionItemKind = completion_item_kind
        self.contextSupport = context_support


class CompletionItemKindClientCapabilities:
    def __init__(self, value_set: Optional[List['CompletionItemKind']] = None):
        self.valueSet = value_set


class CompletionTagSupportClientCapabilities:
    def __init__(self, value_set: Optional[List['CompletionItemTag']] = None):
        self.valueSet = value_set


class CompletionItemClientCapabilities:
    def __init__(self,
                 snippet_support: Optional[bool] = False,
                 commit_character_support: Optional[bool] = False,
                 documentation_format: Optional[List[MarkupKind]] = None,
                 deprecated_support: Optional[bool] = False,
                 preselected_support: Optional[bool] = False,
                 tag_support: Optional[CompletionTagSupportClientCapabilities] = None):
        self.snippetSupport = snippet_support
        self.commitCharacterSupport = commit_character_support
        self.documentationFormat = documentation_format
        self.deprecatedSupport = deprecated_support
        self.preselectedSupport = preselected_support
        self.tagSupport = tag_support


class CompletionOptions(WorkDoneProgressOptions):
    def __init__(self,
                 trigger_characters: Optional[List[str]] = None,
                 all_commit_characters: Optional[List[str]] = None,
                 resolve_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.triggerCharacters = trigger_characters
        self.allCommitCharacters = all_commit_characters
        self.resolveProvider = resolve_provider


class CompletionParams(TextDocumentPositionParams, WorkDoneProgressParams, PartialResultParams):
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position,
                 context: Optional['CompletionContext'] = None,
                 work_done_token: Optional[bool] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        TextDocumentPositionParams.__init__(self, text_document, position)
        WorkDoneProgressParams.__init__(self, work_done_token)
        PartialResultParams.__init__(self, partial_result_token)
        self.context = context


class CompletionTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3


class CompletionContext:
    def __init__(self,
                 trigger_kind: CompletionTriggerKind,
                 trigger_character: Optional[str] = None):
        self.triggerKind = trigger_kind
        self.triggerCharacter = trigger_character


class CompletionList:
    def __init__(self,
                 is_incomplete: bool,
                 items: List['CompletionItem'] = None):
        self.isIncomplete = is_incomplete
        self.items = items if items else []

    def add_item(self, completion_item):
        self.items.append(completion_item)

    def add_items(self, completion_items):
        self.items.extend(completion_items)


class InsertTextFormat(enum.IntEnum):
    PlainText = 1
    Snippet = 2


class CompletionItemTag(enum.IntEnum):
    Deprecated = 1


class CompletionItem:
    def __init__(self,
                 label: str,
                 kind: Optional['CompletionItemKind'] = None,
                 tags: Optional[List[CompletionItemTag]] = None,
                 detail: Optional[str] = None,
                 documentation: Optional[Union[str, MarkupContent]] = None,
                 deprecated: Optional[bool] = False,
                 preselect: Optional[bool] = False,
                 sort_text: Optional[str] = None,
                 filter_text: Optional[str] = None,
                 insert_text: Optional[str] = None,
                 insert_text_format: Optional[InsertTextFormat] = None,
                 text_edit: Optional[TextEdit] = None,
                 additional_text_edits: Optional[List[TextEdit]] = None,
                 commit_characters: Optional[List[str]] = None,
                 command: Optional[Command] = None,
                 data: Optional[Any] = None):
        self.label = label
        self.kind = kind
        self.tags = tags
        self.detail = detail
        self.documentation = documentation
        self.deprecated = deprecated
        self.preselect = preselect
        self.sortText = sort_text
        self.filterText = filter_text
        self.insertText = insert_text
        self.insertTextFormat = insert_text_format
        self.textEdit = text_edit
        self.additionalTextEdits = additional_text_edits
        self.commitCharacters = commit_characters
        self.command = command
        self.data = data


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
