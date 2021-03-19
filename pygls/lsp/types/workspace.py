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

-- Workspace --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Any, List, Optional, Union

from pygls.lsp.types.basic_structures import (Model, NumType, PartialResultParams, Range,
                                              TextDocumentIdentifier, TextDocumentItem,
                                              VersionedTextDocumentIdentifier,
                                              WorkDoneProgressOptions, WorkDoneProgressParams,
                                              WorkspaceEdit)
from pygls.lsp.types.language_features.document_symbol import WorkspaceCapabilitiesSymbolKind


class WorkspaceFoldersServerCapabilities(Model):
    supported: Optional[bool] = False
    change_notifications: Optional[Union[bool, str]] = None


class WorkspaceFolder(Model):
    uri: str
    name: str


class WorkspaceFoldersChangeEvent(Model):
    added: List[WorkspaceFolder]
    removed: List[WorkspaceFolder]


class DidChangeWorkspaceFoldersParams(Model):
    event: WorkspaceFoldersChangeEvent


class DidChangeConfigurationClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False


class DidChangeConfigurationParams(Model):
    settings: Any


class ConfigurationItem(Model):
    scope_uri: Optional[str] = None
    section: Optional[str] = None


class ConfigurationParams(Model):
    items: List[ConfigurationItem]


class DidChangeWatchedFilesClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False


class WatchKind(enum.IntFlag):
    Create = 1
    Change = 2
    Delete = 4


class FileSystemWatcher(Model):
    glob_pattern: str
    kind: Optional[WatchKind] = WatchKind.Create | WatchKind.Change | WatchKind.Delete


class DidChangeWatchedFilesRegistrationOptions(Model):
    watchers: List[FileSystemWatcher]


class FileChangeType(enum.IntEnum):
    Created = 1
    Changed = 2
    Deleted = 3


class FileEvent(Model):
    uri: str
    type: FileChangeType


class DidChangeWatchedFilesParams(Model):
    changes: List[FileEvent]


class WorkspaceSymbolClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    symbol_kind: Optional[WorkspaceCapabilitiesSymbolKind] = None


class WorkspaceSymbolOptions(WorkDoneProgressOptions):
    pass


class WorkspaceSymbolRegistrationOptions(WorkspaceSymbolOptions):
    pass


class WorkspaceSymbolParams(WorkDoneProgressParams, PartialResultParams):
    query: str


class ExecuteCommandClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False


class ExecuteCommandOptions(WorkDoneProgressOptions):
    commands: List[str]


class ExecuteCommandRegistrationOptions(ExecuteCommandOptions):
    pass


class ExecuteCommandParams(WorkDoneProgressParams):
    command: str
    arguments: Optional[List[Any]] = None


class ApplyWorkspaceEditParams(Model):
    edit: WorkspaceEdit
    label: Optional[str] = None


class ApplyWorkspaceEditResponse(Model):
    applied: bool
    failure_reason: Optional[str] = None


class DidOpenTextDocumentParams(Model):
    text_document: TextDocumentItem


class TextDocumentContentChangeEvent(Model):
    range: Optional[Range] = None
    range_length: Optional[NumType] = None
    text: str = ''


class TextDocumentContentChangeTextEvent(Model):
    text: str


class DidChangeTextDocumentParams(Model):
    text_document: VersionedTextDocumentIdentifier
    content_changes: Union[List[TextDocumentContentChangeEvent],
                           List[TextDocumentContentChangeTextEvent]]


class TextDocumentSaveReason(enum.IntEnum):
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class WillSaveTextDocumentParams(Model):
    text_document: TextDocumentIdentifier
    reason: TextDocumentSaveReason


class SaveOptions(Model):
    include_text: bool = False


class DidSaveTextDocumentParams(Model):
    text_document: TextDocumentIdentifier
    text: Optional[str] = None


class DidCloseTextDocumentParams(Model):
    text_document: TextDocumentIdentifier


class TextDocumentSyncClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    will_save: Optional[bool] = False
    will_save_wait_until: Optional[bool] = False
    did_save: Optional[bool] = False
