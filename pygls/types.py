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

Class attributes are named with camel-case notation because client is expecting
that.

Some classes (e.g. `Unregister` and `Unregistration`) are used to match similar
usage in the Language Server Protocol (LSP) documentation.

https://microsoft.github.io/language-server-protocol/specification#client_unregisterCapability
"""


import enum
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from .features import (CODE_ACTION, CODE_LENS, CODE_LENS_RESOLVE, COMPLETION,
                       COMPLETION_ITEM_RESOLVE, DEFINITION, DOCUMENT_HIGHLIGHT, DOCUMENT_LINK,
                       DOCUMENT_LINK_RESOLVE, DOCUMENT_SYMBOL, FORMATTING, HOVER,
                       ON_TYPE_FORMATTING, RANGE_FORMATTING, REFERENCES, RENAME, SIGNATURE_HELP,
                       WORKSPACE_SYMBOL)

# Classes used for type hints.
ConfigCallbackType = Optional[Callable[[List[Any]], None]]
DocumentChangesType = Union[List['TextDocumentEdit'],
                            'TextDocumentEdit',
                            'CreateFile', 'RenameFile', 'DeleteFile']
DocumentSelectorType = List['DocumentFilter']
NumType = Union[int, float]

T = TypeVar('T')

class Undefined(enum.Enum):
    '''Equivalent to Javascript's undefined'''
    token = 0


# https://www.typescriptlang.org/docs/handbook/interfaces.html#optional-properties
OptionalProperty = Union[Undefined, T]

undefined = Undefined.token


class ApplyWorkspaceEditParams:
    def __init__(self,
                 edit: 'WorkspaceEdit',
                 label: OptionalProperty[str] = undefined):
        self.edit = edit
        self.label = label


class ApplyWorkspaceEditResponse:
    def __init__(self,
                 applied: bool,
                 failure_reason: OptionalProperty[str]):
        self.applied = applied
        self.failureReason = failure_reason


class ClientCapabilities:
    def __init__(self,
                 workspace: OptionalProperty['WorkspaceClientCapabilities'] = undefined,
                 text_document: OptionalProperty['TextDocumentClientCapabilities'] = undefined,
                 experimental: OptionalProperty[Any] = undefined):
        self.workspace = workspace
        self.textDocument = text_document
        self.experimental = experimental


class CodeAction:
    def __init__(self,
                 title: str,
                 kind: OptionalProperty['CodeActionKind'] = undefined,
                 diagnostics: OptionalProperty[List['Diagnostic']] = undefined,
                 edit: OptionalProperty['WorkspaceEdit'] = undefined,
                 command: OptionalProperty['Command'] = undefined,
                 is_preferred: OptionalProperty[bool] = undefined):
        self.title = title
        self.kind = kind
        self.diagnostics = diagnostics
        self.edit = edit
        self.command = command
        self.isPreferred = is_preferred


class CodeActionAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 code_action_literal_support:
                 'CodeActionLiteralSupportAbstract'):
        self.dynamicRegistration = dynamic_registration
        self.codeActionLiteralSupport = code_action_literal_support


class CodeActionContext:
    def __init__(self, diagnostics: List['Diagnostic'],
                 only: OptionalProperty[List['CodeActionKind']] = undefined):
        self.diagnostics = diagnostics
        self.only = only


class CodeActionKind(str, enum.Enum):
    QuickFix = 'quickfix'
    Refactor = 'refactor'
    RefactorExtract = 'refactor.extract'
    RefactorInline = 'refactor.inline'
    RefactorRewrite = 'refactor.rewrite'
    Source = 'source'
    SourceOrganizeImports = 'source.organizeImports'


class CodeActionKindAbstract:
    def __init__(self, value_set: List[str]):
        self.valueSet = value_set


class CodeActionLiteralSupportAbstract:
    def __init__(self, code_action_kind: CodeActionKindAbstract):
        self.codeActionKind = code_action_kind


class CodeActionOptions:
    def __init__(self,
                 code_action_kinds:
                 OptionalProperty[List[CodeActionKind]] = undefined):
        self.codeActionKinds = code_action_kinds


class CodeActionParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 range: 'Range',
                 context: CodeActionContext):
        self.textDocument = text_document
        self.range = range
        self.context = context


class CodeLens:
    def __init__(self,
                 range: 'Range',
                 command: OptionalProperty['Command'] = undefined,
                 data: OptionalProperty[Any] = undefined):
        self.range = range
        self.command = command
        self.data = data


class CodeLensOptions:
    def __init__(self, resolve_provider: OptionalProperty[bool] = undefined):
        self.resolveProvider = resolve_provider


class CodeLensParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class Color:
    def __init__(self, red: float, green: float, blue: float, alpha: float):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha


class ColorInformation:
    def __init__(self, range: 'Range', color: Color):
        self.range = range
        self.color = color


class ColorPresentation:
    def __init__(self,
                 label: str,
                 text_edit: OptionalProperty['TextEdit'] = undefined,
                 additional_text_edits:
                 OptionalProperty[List['TextEdit']] = undefined):
        self.label = label
        self.textEdit = text_edit
        self.additionalTextEdits = additional_text_edits


class ColorPresentationParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 color: Color,
                 range: 'Range'):
        self.textDocument = text_document
        self.color = color
        self.range = range


class ColorProviderOptions:
    pass


class Command:
    def __init__(self, title: str, command: str,
                 arguments: OptionalProperty[List[Any]] = undefined):
        self.title = title
        self.command = command
        self.arguments = arguments


class CompletionAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 completion_item: 'CompletionItemAbstract',
                 completion_item_kind: 'CompletionItemKindAbstract',
                 context_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.completionItem = completion_item
        self.completionItemKind = completion_item_kind
        self.contextSupport = context_support


class CompletionContext:
    def __init__(self,
                 trigger_kind: 'CompletionTriggerKind',
                 trigger_character: OptionalProperty[str] = undefined):
        self.triggerKind = trigger_kind
        self.triggerCharacter = trigger_character


class CompletionItem:
    def __init__(self,
                 label: str,
                 kind: OptionalProperty['CompletionItemKind'] = undefined,
                 detail: OptionalProperty[str] = undefined,
                 documentation:
                 OptionalProperty[Union[str, 'MarkupContent']] = undefined,
                 deprecated: OptionalProperty[bool] = undefined,
                 preselect: OptionalProperty[bool] = undefined,
                 sort_text: OptionalProperty[str] = undefined,
                 filter_text: OptionalProperty[str] = undefined,
                 insert_text: OptionalProperty[str] = undefined,
                 insert_text_format:
                 OptionalProperty['InsertTextFormat'] = undefined,
                 text_edit: OptionalProperty['TextEdit'] = undefined,
                 additional_text_edits:
                 OptionalProperty[List['TextEdit']] = undefined,
                 commit_characters: OptionalProperty[List[str]] = undefined,
                 command: OptionalProperty[Command] = undefined,
                 data: OptionalProperty[Any] = undefined):
        self.label = label
        self.kind = kind
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


class CompletionItemAbstract:
    def __init__(self,
                 snippet_support: bool,
                 commit_character_support: bool,
                 documentation_format: List['MarkupKind'],
                 deprecated_support: bool,
                 preselected_support: bool):
        self.snippetSupport = snippet_support
        self.commitCharacterSupport = commit_character_support
        self.documentationFormat = documentation_format
        self.deprecatedSupport = deprecated_support
        self.preselectedSupport = preselected_support


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


class CompletionItemKindAbstract:
    def __init__(self, value_set: List['CompletionItemKind']):
        self.valueSet = value_set


class CompletionList:
    def __init__(self,
                 is_incomplete: bool,
                 items: List[CompletionItem] = None):
        self.isIncomplete = is_incomplete
        self.items = items if items else []

    def add_item(self, completion_item):
        self.items.append(completion_item)

    def add_items(self, completion_items):
        self.items.extend(completion_items)


class CompletionOptions:
    def __init__(self,
                 resolve_provider: OptionalProperty[bool] = undefined,
                 trigger_characters: OptionalProperty[List[str]] = undefined,
                 all_commit_characters:
                 OptionalProperty[List[str]] = undefined):
        self.resolveProvider = resolve_provider
        self.triggerCharacters = trigger_characters
        self.allCommitCharacters = all_commit_characters


class CompletionRegistrationOptions:
    def __init__(self,
                 resolve_provider: OptionalProperty[bool] = undefined,
                 trigger_characters: OptionalProperty[List[str]] = undefined):
        self.resolveProvider = resolve_provider
        self.triggerCharacters = trigger_characters


class CompletionTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3


class ConfigurationItem:
    def __init__(self,
                 scope_uri: OptionalProperty[str] = undefined,
                 section: OptionalProperty[str] = undefined):
        self.scopeUri = scope_uri
        self.section = section


class ConfigurationParams:
    def __init__(self, items: List[ConfigurationItem]):
        self.items = items


class CreateFile:
    def __init__(self,
                 uri: str,
                 options: OptionalProperty['CreateFileOptions'] = undefined):
        self.kind = 'create'
        self.uri = uri
        self.options = options


class CreateFileOptions:
    def __init__(self,
                 overwrite: OptionalProperty[bool] = undefined,
                 ignore_if_exists: OptionalProperty[bool] = undefined):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class DeleteFile:
    def __init__(self,
                 uri: str,
                 options: OptionalProperty['DeleteFileOptions'] = undefined):
        self.kind = 'delete'
        self.uri = uri
        self.options = options


class DeleteFileOptions:
    def __init__(self,
                 recursive: OptionalProperty[bool] = undefined,
                 ignore_if_exists: OptionalProperty[bool] = undefined):
        self.recursive = recursive
        self.ignore_if_exists = ignore_if_exists


class DiagnosticSeverity(enum.IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class Diagnostic:
    def __init__(self,
                 range: 'Range',
                 message: str,
                 severity: OptionalProperty[DiagnosticSeverity] = undefined,
                 code: OptionalProperty[str] = undefined,
                 source: OptionalProperty[str] = undefined,
                 related_information:
                 OptionalProperty[List['DiagnosticRelatedInformation']] =
                 undefined):
        self.range = range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source
        self.relatedInformation = related_information


class DiagnosticRelatedInformation:
    def __init__(self, location: 'Location', message: str):
        self.location = location
        self.message = message


class DidChangeConfigurationParams:
    def __init__(self, settings: Any):
        self.settings = settings


class DidChangeTextDocumentParams:
    def __init__(self,
                 text_document: 'VersionedTextDocumentIdentifier',
                 content_changes: List['TextDocumentContentChangeEvent']):
        self.textDocument = text_document
        self.contentChanges = content_changes


class DidChangeWatchedFiles:
    def __init__(self, changes: List['FileEvent']):
        self.changes = changes


class DidChangeWatchedFilesRegistrationOptions:
    def __init__(self, watchers: List['FileSystemWatcher']):
        self.watchers = watchers


class DidChangeWorkspaceFoldersParams:
    def __init__(self, event: 'WorkspaceFoldersChangeEvent'):
        self.event = event


class DidCloseTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DidOpenTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentItem'):
        self.textDocument = text_document


class DidSaveTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentIdentifier', text: str):
        self.textDocument = text_document
        self.text = text


class DocumentColorParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DocumentFilter:
    def __init__(self,
                 language: OptionalProperty[str] = undefined,
                 scheme: OptionalProperty[str] = undefined,
                 pattern: OptionalProperty[str] = undefined):
        self.language = language
        self.scheme = scheme
        self.pattern = pattern


class DocumentFormattingParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 options: 'FormattingOptions'):
        self.textDocument = text_document
        self.options = options


class DocumentHighlightKind(enum.IntEnum):
    Text = 1
    Read = 2
    Write = 3


class DocumentHighlight:
    def __init__(self,
                 range: 'Range',
                 kind: OptionalProperty[DocumentHighlightKind] = undefined):
        self.range = range
        self.kind = kind


class DocumentLink:
    def __init__(self,
                 range: 'Range',
                 target: OptionalProperty[str] = undefined,
                 data: OptionalProperty[Any] = undefined):
        self.range = range
        self.target = target
        self.data = data


class DocumentLinkOptions:
    def __init__(self, resolve_provider: OptionalProperty[bool] = undefined):
        self.resolveProvider = resolve_provider


class DocumentLinkParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DocumentOnTypeFormattingOptions:
    def __init__(self,
                 first_trigger_character: str,
                 more_trigger_character:
                 OptionalProperty[List[str]] = undefined):
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_character


class DocumentOnTypeFormattingParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: 'Position',
                 ch: str,
                 options: 'FormattingOptions'):
        self.textDocument = text_document
        self.position = position
        self.ch = ch
        self.options = options


class DocumentRangeFormattingParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 range: 'Range',
                 options: 'FormattingOptions'):
        self.textDocument = text_document
        self.range = range
        self.options = options


class DocumentSymbol:
    def __init__(self,
                 name: str,
                 kind: 'SymbolKind',
                 range: 'Range',
                 selection_range: 'Range',
                 detail: OptionalProperty[str] = undefined,
                 children:
                 OptionalProperty[List['DocumentSymbol']] = undefined,
                 deprecated: OptionalProperty[bool] = undefined):
        self.name = name
        self.kind = kind
        self.range = range
        self.selectionRange = selection_range
        self.detail = detail
        self.children = children
        self.deprecated = deprecated


class DocumentSymbolAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 symbol_kind: 'SymbolKindAbstract',
                 hierarchical_document_symbol_support: bool):
        self.dynamicRegistration = dynamic_registration,
        self.symbolKind = symbol_kind
        self.hierarchicalDocumentSymbolSupport = \
            hierarchical_document_symbol_support


class DocumentSymbolParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DynamicRegistrationAbstract:
    def __init__(self, dynamic_registration: bool):
        self.dynamicRegistration = dynamic_registration


class ExecuteCommandOptions:
    def __init__(self, commands: List[str]):
        self.commands = commands


class FailureHandlingKind(str, enum.Enum):
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    Undo = 'undo'


class FileChangeType(enum.IntEnum):
    Created = 1
    Changed = 2
    Deleted = 3


class FileEvent:
    def __init__(self, uri: str, type: FileChangeType):
        self.uri = uri
        self.type = type


if sys.version_info >= (3, 6):
    class WatchKind(enum.IntFlag):
        Create = 1
        Change = 2
        Delete = 4
    _WatchKindType = WatchKind
else:
    # BBB python 3.5 does not have enum.IntFlag
    class WatchKind:
        Create = 1
        Change = 2
        Delete = 4
    _WatchKindType = int


class FileSystemWatcher:
    def __init__(self,
                 glob_pattern: str,
                 kind: OptionalProperty[_WatchKindType] = undefined):
        self.globPattern = glob_pattern
        self.kind = kind


class FoldingRange:
    def __init__(self,
                 start_line: int,
                 end_line: int,
                 start_character: OptionalProperty[int] = undefined,
                 end_character: OptionalProperty[int] = undefined,
                 kind: OptionalProperty['FoldingRangeKind'] = undefined):
        self.startLine = start_line
        self.startCharacter = start_character
        self.endLine = end_line
        self.endCharacter = end_character
        self.kind = kind


class FoldingRangeAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 range_limit: NumType,
                 line_folding_only: bool):
        self.dynamicRegistration = dynamic_registration
        self.rangeLimit = range_limit
        self.lineFoldingOnly = line_folding_only


class FoldingRangeKind(str, enum.Enum):
    Comment = 'comment'
    Imports = 'imports'
    Region = 'region'


class FoldingRangeParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class FormattingOptions:
    def __init__(self,
                 tab_size: int,
                 insert_spaces: bool,
                 **kwargs
                 ):
        self.tabSize = tab_size
        self.insertSpaces = insert_spaces
        self.kwargs = kwargs


class Hover:
    def __init__(self,
                 contents: Any,
                 range: OptionalProperty['Range'] = undefined):
        self.contents = contents
        self.range = range


class HoverAbstract:
    def __init__(self, dynamic_registration,
                 content_format: List['MarkupKind']):
        self.dynamicRegistration = dynamic_registration
        self.contentFormat = content_format


class Trace(str, enum.Enum):
    Off = 'off'
    Messages = 'messages'
    Verbose = 'verbose'


class ClientInfo:
    def __init__(self,
                 name: str = 'unknown',
                 version: OptionalProperty[Optional[str]] = undefined):
        self.name = name
        self.version = version


class InitializeParams:
    def __init__(self,
                 process_id: Optional[int],
                 capabilities: ClientCapabilities,
                 client_info: OptionalProperty[ClientInfo] = undefined,
                 root_uri: Optional[str] = None,
                 root_path: Optional[str] = None,
                 initialization_options: OptionalProperty[Any] = undefined,
                 trace: OptionalProperty[Trace] = undefined,
                 workspace_folders:
                 OptionalProperty[Optional[List['WorkspaceFolder']]] =
                 undefined) -> None:
        self.processId = process_id
        self.clientInfo = client_info
        self.rootPath = root_path
        self.rootUri = root_uri
        self.initializationOptions = initialization_options
        self.capabilities = capabilities
        self.trace = trace
        self.workspaceFolders = workspace_folders


class InitializeResult:
    def __init__(self, capabilities: 'ServerCapabilities'):
        self.capabilities = capabilities


class InsertTextFormat(enum.IntEnum):
    PlainText = 1
    Snippet = 2


class Location:
    def __init__(self, uri: str, range: 'Range'):
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
                 target_range: 'Range',
                 target_selection_range: 'Range',
                 origin_selection_range:
                 OptionalProperty['Range'] = undefined):
        self.targetUri = target_uri
        self.targetRange = target_range
        self.targetSelectionRange = target_selection_range
        self.originSelectionRange = origin_selection_range


class LogMessageParams:
    def __init__(self, type: NumType, message: str):
        self.type = type
        self.message = message


class MarkupContent:
    def __init__(self, kind: 'MarkupKind', value: str):
        self.kind = kind
        self.value = value


class MarkupKind(str, enum.Enum):
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MessageActionItem:
    def __init__(self, title: str):
        self.title = title


class MessageType(enum.IntEnum):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class ExecuteCommandParams:
    def __init__(self,
                 command: str,
                 arguments: OptionalProperty[List[object]] = undefined):
        self.command = command
        self.arguments = arguments


class ExecuteCommandRegistrationOptions:
    def __init__(self, commands: List[str]):
        self.commands = commands


class ParameterInformation:
    def __init__(self,
                 label: str,
                 documentation:
                 OptionalProperty[Union[str, MarkupContent]] = undefined):
        self.label = label
        self.documentation = documentation


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


class PublishDiagnosticsAbstract:
    def __init__(self, related_information: bool):
        self.relatedInformation = related_information


class PublishDiagnosticsParams:
    def __init__(self, uri: str, diagnostics: List[Diagnostic]):
        self.uri = uri
        self.diagnostics = diagnostics


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


class ReferenceContext:
    def __init__(self, include_declaration: bool):
        self.includeDeclaration = include_declaration


class Registration:
    def __init__(self,
                 id: str,
                 method: str,
                 register_options: OptionalProperty[Any] = undefined):
        self.id = id
        self.method = method
        self.registerOptions = register_options


class RegistrationParams:
    def __init__(self, registrations: List[Registration]):
        self.registrations = registrations


class RenameAbstract:
    def __init__(self, dynamic_registration: bool, prepare_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.prepareSupport = prepare_support


class RenameFile:
    def __init__(self,
                 old_uri: str,
                 new_uri: str,
                 options: OptionalProperty['RenameFileOptions'] = undefined):
        self.kind = 'rename'
        self.old_uri = old_uri
        self.new_uri = new_uri
        self.options = options


class RenameFileOptions:
    def __init__(self,
                 overwrite: OptionalProperty[bool] = undefined,
                 ignore_if_exists: OptionalProperty[bool] = undefined):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class RenameParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: Position,
                 new_name: str):
        self.textDocument = text_document
        self.position = position
        self.newName = new_name


class ResourceOperationKind(str, enum.Enum):
    Create = 'create'
    Rename = 'rename'
    Delete = 'delete'


class SaveOptions:
    def __init__(self, include_text: OptionalProperty[bool] = undefined):
        self.includeText = include_text


class ServerCapabilities:
    def __init__(self,
                 features,
                 feature_options,
                 commands,
                 sync_kind,
                 client_capabilities):
        self.textDocumentSync = sync_kind
        self.hoverProvider = HOVER in features

        if COMPLETION in features:
            self.completionProvider = CompletionOptions(
                resolve_provider=COMPLETION_ITEM_RESOLVE in features,
                trigger_characters=feature_options.get(
                    COMPLETION, {}).get('trigger_characters', [])
            )

        if SIGNATURE_HELP in features:
            self.signatureHelpProvider = SignatureHelpOptions(
                trigger_characters=feature_options.get(
                    SIGNATURE_HELP, {}).get('trigger_characters', [])
            )

        self.definitionProvider = DEFINITION in features

        self.referencesProvider = REFERENCES in features
        self.documentHighlightProvider = DOCUMENT_HIGHLIGHT in features
        self.documentSymbolProvider = DOCUMENT_SYMBOL in features
        self.workspaceSymbolProvider = WORKSPACE_SYMBOL in features
        self.codeActionProvider = CODE_ACTION in features

        if CODE_LENS in features:
            self.codeLensProvider = CodeLensOptions(
                resolve_provider=CODE_LENS_RESOLVE in features
            )

        self.documentFormattingProvider = FORMATTING in features
        self.documentRangeFormattingProvider = RANGE_FORMATTING in features

        if FORMATTING in features:
            self.documentOnTypeFormattingProvider = \
                DocumentOnTypeFormattingOptions(
                    first_trigger_character=feature_options.get(
                        ON_TYPE_FORMATTING, {})
                    .get('first_trigger_character', ''),

                    more_trigger_character=feature_options.get(
                        ON_TYPE_FORMATTING, {})
                    .get('more_trigger_character', [])
                )

        self.renameProvider = RENAME in features

        if DOCUMENT_LINK in features:
            self.documentLinkProvider = DocumentLinkOptions(
                resolve_provider=DOCUMENT_LINK_RESOLVE in features
            )

        self.executeCommandProvider = ExecuteCommandOptions(
            commands=list(commands.keys())
        )

        self.workspace = {
            'workspaceFolders': {
                'supported': True,
                'changeNotifications': True
            }
        }

    def __repr__(self):
        return '{}( {} )'.format(type(self).__name__, self.__dict__)


class ShowMessageParams:
    def __init__(self, type: MessageType, message: str):
        self.type = type
        self.message = message


class ShowMessageRequestParams:
    def __init__(self,
                 type: MessageType,
                 message: str,
                 actions:
                 OptionalProperty[List[MessageActionItem]] = undefined):
        self.type = type
        self.message = message
        self.actions = actions


class SignatureHelp:
    def __init__(self,
                 signatures: List['SignatureInformation'],
                 active_signature: OptionalProperty[int] = undefined,
                 active_parameter: OptionalProperty[int] = undefined):
        self.signatures = signatures
        self.activeSignature = active_signature
        self.activeParameter = active_parameter


class SignatureHelpAbstract:
    def __init__(self,
                 dynamic_registration: bool = False,
                 signature_information: List[MarkupKind] = None):
        self.dynamicRegistration = dynamic_registration
        self.signatureInformation = signature_information


class SignatureHelpOptions:
    def __init__(self,
                 trigger_characters: OptionalProperty[List[str]] = undefined):
        self.triggerCharacters = trigger_characters


class SignatureInformation:
    def __init__(self,
                 label: str,
                 documentation:
                 OptionalProperty[Union[str, MarkupContent]] = undefined,
                 parameters:
                 OptionalProperty[List[ParameterInformation]] = undefined):
        self.label = label
        self.documentation = documentation
        self.parameters = parameters


class SignatureInformationAbstract:
    def __init__(self, documentation_format: List[MarkupKind]):
        self.documentationFormat = documentation_format


class StaticRegistrationOptions:
    def __init__(self, id: OptionalProperty[str] = undefined):
        self.id = id


class SymbolAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 symbol_kind: 'SymbolKindAbstract'):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind


class SymbolInformation:
    def __init__(self,
                 name: str,
                 kind: int,
                 location: 'Location',
                 container_name: OptionalProperty[str] = undefined,
                 deprecated: OptionalProperty[bool] = undefined):
        self.name = name
        self.kind = kind
        self.location = location
        self.containerName = container_name
        self.deprecated = deprecated


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


class SymbolKindAbstract:
    def __init__(self, value_set: List[SymbolKind]):
        self.valueSet = value_set


class SynchronizationAbstract:
    def __init__(self, dynamic_registration: bool, will_save: bool,
                 will_save_wait_until: bool, did_save: bool):
        self.dynamicRegistration = dynamic_registration
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.didSave = did_save


class TextDocumentClientCapabilities:

    def __init__(self,
                 synchronization: SynchronizationAbstract,
                 completion: CompletionAbstract,
                 hover: HoverAbstract,
                 signature_help: SignatureHelpAbstract,
                 references: DynamicRegistrationAbstract,
                 document_highlight: DynamicRegistrationAbstract,
                 document_symbol: DocumentSymbolAbstract,
                 formatting: DynamicRegistrationAbstract,
                 range_formatting: DynamicRegistrationAbstract,
                 on_type_formatting: DynamicRegistrationAbstract,
                 definition: DynamicRegistrationAbstract,
                 type_definition: DynamicRegistrationAbstract,
                 implementation: DynamicRegistrationAbstract,
                 code_action: CodeActionAbstract,
                 code_lens: DynamicRegistrationAbstract,
                 document_link: DynamicRegistrationAbstract,
                 color_provider: DynamicRegistrationAbstract,
                 rename: RenameAbstract,
                 publish_diagnostics: PublishDiagnosticsAbstract,
                 folding_range: FoldingRangeAbstract):
        self.synchronization = synchronization
        self.completion = completion
        self.hover = hover
        self.signatureHelp = signature_help
        self.references = references
        self.documentHighlight = document_highlight
        self.documentSymbol = document_symbol
        self.formatting = formatting
        self.rangeFormatting = range_formatting
        self.onTypeFormatting = on_type_formatting
        self.definition = definition
        self.typeDefinition = type_definition
        self.implementation = implementation
        self.codeAction = code_action
        self.codeLens = code_lens
        self.documentLink = document_link
        self.colorProvider = color_provider
        self.rename = rename
        self.publishDiagnostics = publish_diagnostics
        self.foldingRange = folding_range


class TextDocumentContentChangeEvent:
    def __init__(self,
                 range: 'Range',
                 range_length: OptionalProperty[NumType] = undefined,
                 text: str = ''):
        self.range = range
        self.rangeLength = range_length
        self.text = text


class TextDocumentEdit:
    def __init__(self,
                 text_document: 'VersionedTextDocumentIdentifier',
                 edits: List['TextEdit']):
        self.textDocument = text_document
        self.edits = edits


class TextDocumentIdentifier:
    def __init__(self, uri: str):
        self.uri = uri


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    def __init__(self, uri: str, version: Optional[NumType] = None):
        super().__init__(uri)
        self.version = version


class TextDocumentItem(VersionedTextDocumentIdentifier):
    def __init__(self,
                 uri: str,
                 language_id: str,
                 version: NumType,
                 text: str):
        super().__init__(uri, version)
        self.languageId = language_id
        self.text = text


class TextDocumentPositionParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: Position):
        self.textDocument = text_document
        self.position = position


class CompletionParams(TextDocumentPositionParams):
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: Position,
                 context: OptionalProperty[CompletionContext] = undefined):
        super().__init__(text_document, position)
        self.context = context


class HoverParams(TextDocumentPositionParams):
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: 'Position'):
        super().__init__(text_document, position)


class ReferenceParams(TextDocumentPositionParams):
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: Position,
                 context: ReferenceContext):
        super().__init__(text_document, position)
        self.context = context


class TextDocumentRegistrationOptions:
    def __init__(self, document_selector: DocumentSelectorType = None):
        self.documentSelector = document_selector


class CodeLensRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 resolve_provider: bool = False):
        super().__init__(document_selector)
        self.resolveProvider = resolve_provider


class DocumentLinkRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 resolve_provider: bool = False):
        super().__init__(document_selector)
        self.resolveProvider = resolve_provider


class DocumentOnTypeFormattingRegistrationOptions(
        TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 first_trigger_character: str = None,
                 more_trigger_characters: OptionalProperty[List[str]] = undefined):
        super().__init__(document_selector)
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_characters


class RenameRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 prepare_provider: OptionalProperty[bool] = undefined):
        super().__init__(document_selector)
        self.prepareProvider = prepare_provider


class SignatureHelpRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 trigger_characters: OptionalProperty[List[str]] = undefined):
        super().__init__(document_selector)
        self.triggerCharacters = trigger_characters


class TextDocumentSaveRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 include_text: OptionalProperty[bool] = undefined):
        super().__init__(document_selector)
        self.includeText = include_text


class TextDocumentSaveReason(enum.IntEnum):
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class TextDocumentSyncKind(enum.IntEnum):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class TextDocumentSyncOptions:
    def __init__(self,
                 open_close: OptionalProperty[bool] = undefined,
                 change: OptionalProperty[TextDocumentSyncKind] = undefined,
                 will_save: OptionalProperty[bool] = undefined,
                 will_save_wait_until: OptionalProperty[bool] = undefined,
                 save: OptionalProperty[SaveOptions] = undefined):
        self.openClose = open_close
        self.change = change
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.save = save


class TextEdit:
    def __init__(self, range: Range, new_text: str):
        self.range = range
        self.newText = new_text


class Unregistration:
    def __init__(self, id: str, method: str):
        self.id = id
        self.method = method


class UnregistrationParams:
    def __init__(self, unregisterations: List[Unregistration]):
        self.unregisterations = unregisterations


class WillSaveTextDocumentParams:
    def __init__(self, text_document: TextDocumentIdentifier, reason: int):
        self.textDocument = text_document
        self.reason = reason


class WorkspaceClientCapabilities:
    def __init__(self,
                 apply_edit: bool,
                 workspace_edit: 'WorkspaceEditCapability',
                 did_change_configuration: DynamicRegistrationAbstract,
                 did_change_watched_files: DynamicRegistrationAbstract,
                 symbol: SymbolAbstract,
                 execute_command: DynamicRegistrationAbstract,
                 workspace_folders: bool,
                 configuration: bool):
        self.applyEdit = apply_edit
        self.workspaceEdit = workspace_edit
        self.didChangeConfiguration = did_change_configuration
        self.didChangeWatched = did_change_watched_files
        self.symbol = symbol
        self.executeCommand = execute_command
        self.workspace_folders = workspace_folders
        self.configuration = configuration


class WorkspaceEdit:
    def __init__(self,
                 changes:
                 OptionalProperty[Dict[str, List[TextEdit]]] = undefined,
                 document_changes:
                 OptionalProperty[DocumentChangesType] = undefined):
        self.changes = changes
        self.documentChanges = document_changes


class WorkspaceEditCapability:
    def __init__(self,
                 document_changes: bool,
                 resource_operations: List[ResourceOperationKind],
                 failure_handling: FailureHandlingKind):
        self.documentChanges = document_changes
        self.resourceOperations = resource_operations
        self.failureHandling = failure_handling


class WorkspaceFolder:
    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name


class WorkspaceFoldersChangeEvent:
    def __init__(self,
                 added: List[WorkspaceFolder],
                 removed: List[WorkspaceFolder]):
        self.added = added
        self.removed = removed


class WorkspaceSymbolParams:
    def __init__(self, query: str):
        self.query = query
