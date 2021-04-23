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
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, root_validator
from typeguard import check_type

NumType = Union[int, float]
T = TypeVar('T')
ProgressToken = Union[int, str]

ConfigCallbackType = Optional[Callable[[List[Any]], None]]


def snake_to_camel(string: str) -> str:
    return ''.join(
        word.capitalize() if idx > 0 else word
        for idx, word in enumerate(string.split('_'))
    )


class Model(BaseModel):
    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class JsonRpcMessage(Model):
    """A base json rpc message defined by LSP."""
    jsonrpc: str


class JsonRPCNotification(JsonRpcMessage):
    """A class that represents json rpc notification message."""
    method: str
    params: Any


class JsonRPCRequestMessage(JsonRpcMessage):
    """A class that represents json rpc request message."""
    id: Any
    method: str
    params: Any

    @root_validator
    def check_result_or_error(cls, values):
        # Workaround until pydantic supports StrictUnion
        # https://github.com/samuelcolvin/pydantic/pull/2092
        id_val = values.get('id')
        check_type('', id_val, Union[int, str])

        return values


class JsonRPCResponseMessage(JsonRpcMessage):
    """A class that represents json rpc response message."""
    id: Any
    result: Any
    error: Any

    @root_validator
    def check_result_or_error(cls, values):
        # Workaround until pydantic supports StrictUnion
        # https://github.com/samuelcolvin/pydantic/pull/2092
        id_val = values.get('id')
        check_type('', id_val, Union[int, str])

        result_val, error_val = values.get('result'), values.get('error')

        if result_val is not None and error_val is not None:
            raise ValueError('Fields "result" and "error" are both set!')

        return values


class Position(Model):
    line: int
    character: int

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
        return f'{self.line}:{self.character}'


class Range(Model):
    start: Position
    end: Position

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
        return f'{self.start!r}-{self.end!r}'


class Location(Model):
    uri: str
    range: Range

    def __eq__(self, other):
        return (
            isinstance(other, Location)
            and self.uri == other.uri
            and self.range == other.range)

    def __repr__(self):
        return f"{self.uri}:{self.range!r}"


class LocationLink(Model):
    target_uri: str
    target_range: Range
    target_selection_range: Range
    origin_selection_range: Optional[Range] = None


class DiagnosticSeverity(enum.IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class DiagnosticTag(enum.IntEnum):
    Unnecessary = 1
    Deprecated = 2


class DiagnosticRelatedInformation(Model):
    location: Location
    message: str


class Diagnostic(Model):
    range: Range
    message: str
    severity: Optional[DiagnosticSeverity] = None
    code: Optional[Union[int, str]] = None
    source: Optional[str] = None
    related_information: Optional[List[DiagnosticRelatedInformation]] = None
    tags: Optional[List[DiagnosticTag]] = None


class Command(Model):
    title: str
    command: str
    arguments: Optional[List[Any]] = None


class TextEdit(Model):
    range: Range
    new_text: str


class ResourceOperationKind(str, enum.Enum):
    Create = 'create'
    Rename = 'rename'
    Delete = 'delete'


class CreateFileOptions(Model):
    overwrite: Optional[bool] = False
    ignore_if_exists: Optional[bool] = False


class CreateFile(Model):
    kind: ResourceOperationKind = ResourceOperationKind.Create
    uri: str
    options: Optional[CreateFileOptions] = None


class RenameFileOptions(Model):
    overwrite: Optional[bool] = False
    ignore_if_exists: Optional[bool] = False


class RenameFile(Model):
    kind: ResourceOperationKind = ResourceOperationKind.Rename
    old_uri: str
    new_uri: str
    options: Optional[RenameFileOptions] = None


class DeleteFileOptions(Model):
    recursive: Optional[bool] = False
    ignore_if_exists: Optional[bool] = False


class DeleteFile(Model):
    kind: ResourceOperationKind = ResourceOperationKind.Delete
    uri: str
    options: Optional[DeleteFileOptions] = None


class FailureHandlingKind(str, enum.Enum):
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    Undo = 'undo'


class WorkspaceEditClientCapabilities(Model):
    document_changes: Optional[bool] = False
    resource_operations: Optional[List[ResourceOperationKind]] = None
    failure_handling: Optional[FailureHandlingKind] = None


class TextDocumentIdentifier(Model):
    uri: str


class TextDocumentItem(Model):
    uri: str
    language_id: str
    version: NumType
    text: str


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    version: NumType


class OptionalVersionedTextDocumentIdentifier(TextDocumentIdentifier):
    version: Optional[NumType]


class TextDocumentEdit(Model):
    text_document: OptionalVersionedTextDocumentIdentifier
    edits: List[TextEdit]


class TextDocumentPositionParams(Model):
    text_document: TextDocumentIdentifier
    position: Position


class DocumentFilter(Model):
    language: Optional[str] = None
    scheme: Optional[str] = None
    pattern: Optional[str] = None


DocumentSelector = List[DocumentFilter]


class StaticRegistrationOptions(Model):
    id: Optional[str] = None


class TextDocumentRegistrationOptions(Model):
    document_selector: Optional[DocumentSelector] = None


class MarkupKind(str, enum.Enum):
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MarkupContent(Model):
    kind: MarkupKind
    value: str


class WorkspaceEdit(Model):
    changes: Optional[Dict[str, List[TextEdit]]] = None
    document_changes: Any = None

    @root_validator
    def check_result_or_error(cls, values):
        # Workaround until pydantic supports StrictUnion
        # https://github.com/samuelcolvin/pydantic/pull/2092

        document_changes_val = values.get('document_changes')
        check_type(
            '',
            document_changes_val,
            Optional[Union[
                List[TextDocumentEdit],
                List[Union[TextDocumentEdit, CreateFile, RenameFile, DeleteFile]],
            ]]
        )

        return values


class WorkDoneProgressBegin(Model):
    kind: str = 'begin'
    title: str
    cancellable: Optional[bool] = False
    message: Optional[str] = None
    percentage: Optional[NumType] = None


class WorkDoneProgressReport(Model):
    kind: str = 'report'
    cancellable: Optional[bool] = False
    message: Optional[str] = None
    percentage: Optional[NumType] = None


class WorkDoneProgressEnd(Model):
    kind: str = 'end'
    message: Optional[str] = None


class WorkDoneProgressParams(Model):
    work_done_token: Optional[ProgressToken]


class WorkDoneProgressOptions(Model):
    work_done_progress: Optional[ProgressToken]


class PartialResultParams(Model):
    partial_result_token: Optional[ProgressToken]
