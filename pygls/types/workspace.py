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
import sys
from typing import Any, List, Optional, Union

from pygls.types.basic_structures import (NumType, PartialResultParams, ProgressToken, Range,
                                          TextDocumentIdentifier, TextDocumentItem,
                                          VersionedTextDocumentIdentifier, WorkDoneProgressOptions,
                                          WorkDoneProgressParams, WorkspaceEdit)


class WorkspaceFoldersServerCapabilities:
    def __init__(self,
                 supported: Optional[bool] = False,
                 change_notifications: Optional[Union[str, bool]] = None):
        self.supported = supported
        self.changeNotifications = change_notifications


class WorkspaceFolder:
    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name


class DidChangeWorkspaceFoldersParams:
    def __init__(self, event: 'WorkspaceFoldersChangeEvent'):
        self.event = event


class WorkspaceFoldersChangeEvent:
    def __init__(self,
                 added: List[WorkspaceFolder],
                 removed: List[WorkspaceFolder]):
        self.added = added
        self.removed = removed


class DidChangeConfigurationClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DidChangeConfigurationParams:
    def __init__(self, settings: Any):
        self.settings = settings


class ConfigurationParams:
    def __init__(self, items: List[ConfigurationItem]):
        self.items = items


class ConfigurationItem:
    def __init__(self,
                 scope_uri: Optional[str] = None,
                 section: Optional[str] = None):
        self.scopeUri = scope_uri
        self.section = section


class DidChangeWatchedFilesClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DidChangeWatchedFilesRegistrationOptions:
    def __init__(self, watchers: List[FileSystemWatcher]):
        self.watchers = watchers


class FileSystemWatcher:
    def __init__(self,
                 glob_pattern: str,
                 kind: Optional[WatchKindType] = WatchKind.Create | WatchKind.Change | WatchKind.Delete):
        self.globPattern = glob_pattern
        self.kind = kind


if sys.version_info >= (3, 6):
    class WatchKind(enum.IntFlag):
        Create = 1
        Change = 2
        Delete = 4
    WatchKindType = WatchKind
else:
    # python 3.5 does not have enum.IntFlag
    class WatchKind:
        Create = 1
        Change = 2
        Delete = 4
    WatchKindType = int


class DidChangeWatchedFilesParams:
    def __init__(self, changes: List[FileEvent]):
        self.changes = changes


class FileEvent:
    def __init__(self, uri: str, type: 'FileChangeType'):
        self.uri = uri
        self.type = type


class FileChangeType(enum.IntEnum):
    Created = 1
    Changed = 2
    Deleted = 3


class WorkspaceSymbolClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 symbol_kind: Optional['WorkspaceCapabilitiesSymbolKind'] = None):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind


class WorkspaceSymbolOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class WorkspaceSymbolRegistrationOptions(WorkspaceSymbolOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class WorkspaceSymbolParams(WorkDoneProgressParams, PartialResultParams):
    def __init__(self, query: str,
                 work_done_progress: Optional[ProgressToken] = None,
                 partial_result_token: Optional[ProgressToken] = None):
        WorkDoneProgressParams.__init__(work_done_progress)
        PartialResultParams.__init__(partial_result_token)
        self.query = query


class ExecuteCommandClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class ExecuteCommandOptions(WorkDoneProgressOptions):
    def __init__(self,
                 commands: List[str],
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.commands = commands


class ExecuteCommandRegistrationOptions(WorkDoneProgressOptions):
    def __init__(self, commands: List[str], work_done_progress: Optional[ProgressToken] = None):
        super().__init__(commands, work_done_progress=work_done_progress)


class ExecuteCommandParams(WorkDoneProgressParams):
    def __init__(self,
                 command: str,
                 arguments: Optional[List[Any]] = None,
                 work_done_token: Optional[bool] = None):
        super().__init__(work_done_token)
        self.command = command
        self.arguments = arguments


class ApplyWorkspaceEditParams:
    def __init__(self, edit: WorkspaceEdit, label: Optional[str] = None):
        self.edit = edit
        self.label = label


class ApplyWorkspaceEditResponse:
    def __init__(self, applied: bool, failure_reason: Optional[str] = None):
        self.applied = applied
        self.failureReason = failure_reason


class DidOpenTextDocumentParams:
    def __init__(self, text_document: TextDocumentItem):
        self.textDocument = text_document


class DidChangeTextDocumentParams:
    def __init__(self,
                 text_document: VersionedTextDocumentIdentifier,
                 content_changes: List[TextDocumentContentChangeEvent]):
        self.textDocument = text_document
        self.contentChanges = content_changes


class TextDocumentContentChangeEvent:
    def __init__(self,
                 range: Optional[Range] = None,  # because of {'text': ''}
                 range_length: Optional[NumType] = None,
                 text: str = ''):
        self.range = range
        self.rangeLength = range_length
        self.text = text


class WillSaveTextDocumentParams:
    def __init__(self, text_document: TextDocumentIdentifier, reason: int):
        self.textDocument = text_document
        self.reason = reason


class TextDocumentSaveReason(enum.IntEnum):
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class SaveOptions:
    def __init__(self, include_text: bool = False):
        self.includeText = include_text


class DidSaveTextDocumentParams:
    def __init__(self, text_document: TextDocumentIdentifier, text: Optional[str] = None):
        self.textDocument = text_document
        self.text = text


class DidCloseTextDocumentParams:
    def __init__(self, text_document: TextDocumentIdentifier):
        self.textDocument = text_document


class TextDocumentSyncClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 will_save: Optional[bool] = False,
                 will_save_wait_until: Optional[bool] = False,
                 did_save: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.didSave = did_save
