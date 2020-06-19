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

-- Basic Structures --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

NumType = Union[int, float]
T = TypeVar('T')
ProgressToken = Union[int, str]

ConfigCallbackType = Optional[Callable[[List[Any]], None]]
DocumentChangesType = Union[List['TextDocumentEdit'],
                            'TextDocumentEdit',
                            'CreateFile', 'RenameFile', 'DeleteFile']


class Position:
    def __init__(self, line: int = 0, character: int = 0):
        self.line = line
        self.character = character

    def __eq__(self, other):
        return (
            isinstance(other, Position)
            and self.line == other.line
            and self.character == other.character)

    def __ge__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character >= other.character

        return False

    def __gt__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character > other.character

        return False

    def __le__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character <= other.character

        return False

    def __lt__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character < other.character

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.line, self.character))

    def __iter__(self):
        return iter((self.line, self.character))

    def __repr__(self):
        return '{}:{}'.format(self.line, self.character)


class Range:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __eq__(self, other):
        return (
            isinstance(other, Range)
            and self.start == other.start
            and self.end == other.end)

    def __hash__(self):
        return hash((self.start, self.end))

    def __iter__(self):
        return iter((self.start, self.end))

    def __repr__(self):
        return '{}-{}'.format(self.start, self.end)


class Location:
    def __init__(self, uri: str, range: Range):
        self.uri = uri
        self.range = range

    def __eq__(self, other):
        return (
            isinstance(other, Location)
            and self.uri == other.uri
            and self.range == other.range)

    def __repr__(self):
        return "{}:{}".format(self.uri, self.range)


class LocationLink:
    def __init__(self,
                 target_uri: str,
                 target_range: Range,
                 target_selection_range: Range,
                 origin_selection_range: Optional[Range] = None):
        self.targetUri = target_uri
        self.targetRange = target_range
        self.targetSelectionRange = target_selection_range
        self.originSelectionRange = origin_selection_range


class Diagnostic:
    def __init__(self,
                 range: Range,
                 message: str,
                 severity: Optional[DiagnosticSeverity] = None,
                 code: Optional[Union[int, str]] = None,
                 source: Optional[str] = None,
                 related_information: Optional[List['DiagnosticRelatedInformation']] = None,
                 tags: Optional[List['DiagnosticTag']] = None):
        self.range = range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source
        self.relatedInformation = related_information
        self.tags = tags


class DiagnosticSeverity(enum.IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class DiagnosticTag(enum.IntEnum):
    Unnecessary = 1
    Deprecated = 2


class DiagnosticRelatedInformation:
    def __init__(self, location: 'Location', message: str):
        self.location = location
        self.message = message


class Command:
    def __init__(self, title: str, command: str, arguments: Optional[List[Any]] = None):
        self.title = title
        self.command = command
        self.arguments = arguments


class TextEdit:
    def __init__(self, range: Range, new_text: str):
        self.range = range
        self.newText = new_text


class TextDocumentEdit:
    def __init__(self,
                 text_document: 'VersionedTextDocumentIdentifier',
                 edits: List[TextEdit]):
        self.textDocument = text_document
        self.edits = edits


class CreateFileOptions:
    def __init__(self,
                 overwrite: Optional[bool] = False,
                 ignore_if_exists: Optional[bool] = False):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class CreateFile:
    def __init__(self,
                 uri: str,
                 options: Optional[CreateFileOptions] = None):
        self.kind = 'create'
        self.uri = uri
        self.options = options


class RenameFileOptions:
    def __init__(self,
                 overwrite: Optional[bool] = False,
                 ignore_if_exists: Optional[bool] = False):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class RenameFile:
    def __init__(self,
                 old_uri: str,
                 new_uri: str,
                 options: Optional[RenameFileOptions] = None):
        self.kind = 'rename'
        self.old_uri = old_uri
        self.new_uri = new_uri
        self.options = options


class DeleteFileOptions:
    def __init__(self,
                 recursive: Optional[bool] = False,
                 ignore_if_exists: Optional[bool] = False):
        self.recursive = recursive
        self.ignore_if_exists = ignore_if_exists


class DeleteFile:
    def __init__(self,
                 uri: str,
                 options: Optional[DeleteFileOptions] = None):
        self.kind = 'delete'
        self.uri = uri
        self.options = options


class WorkspaceEdit:
    def __init__(self,
                 changes: Optional[Dict[str, List[TextEdit]]] = None,
                 document_changes: Optional[DocumentChangesType] = None):
        self.changes = changes
        self.documentChanges = document_changes


class WorkspaceEditClientCapabilities:
    def __init__(self,
                 document_changes: Optional[bool] = False,
                 resource_operations: Optional[List[ResourceOperationKind]] = None,
                 failure_handling: Optional[FailureHandlingKind] = None):
        self.documentChanges = document_changes
        self.resourceOperations = resource_operations
        self.failureHandling = failure_handling


class ResourceOperationKind(str, enum.Enum):
    Create = 'create'
    Rename = 'rename'
    Delete = 'delete'


class FailureHandlingKind(str, enum.Enum):
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    Undo = 'undo'


class TextDocumentIdentifier:
    def __init__(self, uri: str):
        self.uri = uri


class TextDocumentItem:
    def __init__(self,
                 uri: str,
                 language_id: str,
                 version: NumType,
                 text: str):
        self.uri = uri
        self.languageId = language_id
        self.version = version
        self.text = text


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    def __init__(self, uri: str, version: Union[NumType, None]):
        super().__init__(uri)
        self.version = version


class TextDocumentPositionParams:
    def __init__(self,
                 text_document: TextDocumentIdentifier,
                 position: Position):
        self.textDocument = text_document
        self.position = position


class DocumentFilter:
    def __init__(self,
                 language: Optional[str] = None,
                 scheme: Optional[str] = None,
                 pattern: Optional[str] = None):
        self.language = language
        self.scheme = scheme
        self.pattern = pattern


DocumentSelector = List['DocumentFilter']


class StaticRegistrationOptions:
    def __init__(self, id: Optional[str] = None):
        self.id = id


class TextDocumentRegistrationOptions:
    def __init__(self, document_selector: Optional[DocumentSelector] = None):
        self.documentSelector = document_selector


class MarkupKind(str, enum.Enum):
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MarkupContent:
    def __init__(self, kind: MarkupKind, value: str):
        self.kind = kind
        self.value = value


class WorkDoneProgressBegin:
    def __init__(self,
                 title: str,
                 cancellable: Optional[bool] = False,
                 message: Optional[str] = None,
                 percentage: Optional[NumType] = None):
        self.kind = 'begin'
        self.title = title
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage


class WorkDoneProgressReport:
    def __init__(self,
                 cancellable: Optional[bool] = False,
                 message: Optional[str] = None,
                 percentage: Optional[NumType] = None):
        self.kind = 'report'
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage


class WorkDoneProgressEnd:
    def __init__(self, message: Optional[str] = None):
        self.kind = 'end'
        self.message = message


class WorkDoneProgressParams:
    def __init__(self, work_done_token: Optional[bool] = None):
        self.workDoneToken = work_done_token


class WorkDoneProgressOptions:
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        self.workDoneProgress = work_done_progress


class PartialResultParams:
    def __init__(self, partial_result_token: Optional[ProgressToken] = None):
        self.partialResultToken = partial_result_token
