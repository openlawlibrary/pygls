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
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

from pygls.features import (CODE_ACTION, CODE_LENS, CODE_LENS_RESOLVE, COMPLETION,
                            COMPLETION_ITEM_RESOLVE, DEFINITION, DOCUMENT_HIGHLIGHT, DOCUMENT_LINK,
                            DOCUMENT_LINK_RESOLVE, DOCUMENT_SYMBOL, FORMATTING, HOVER,
                            ON_TYPE_FORMATTING, RANGE_FORMATTING, REFERENCES, RENAME,
                            SIGNATURE_HELP, WORKSPACE_SYMBOL)

# Classes used for type hints.
ConfigCallbackType = Optional[Callable[[List[Any]], None]]
DocumentChangesType = Union[List['TextDocumentEdit'],
                            'TextDocumentEdit',
                            'CreateFile', 'RenameFile', 'DeleteFile']
DocumentSelectorType = List['DocumentFilter']
NumType = Union[int, float]
T = TypeVar('T')
ProgressToken = Union[int, str]


class ApplyWorkspaceEditParams:
    def __init__(self, edit: 'WorkspaceEdit', label: Optional[str] = None):
        self.edit = edit
        self.label = label


class ApplyWorkspaceEditResponse:
    def __init__(self, applied: bool):
        self.applied = applied


class CodeAction:
    def __init__(self,
                 title: str,
                 kind: 'CodeActionKind' = None,
                 diagnostics: List['Diagnostic'] = None,
                 edit: 'WorkspaceEdit' = None,
                 command: 'Command' = None):
        self.title = title
        self.kind = kind
        self.diagnostics = diagnostics
        self.edit = edit
        self.command = command


class CodeActionContext:
    def __init__(self, diagnostics: List['Diagnostic'],
                 only: List['CodeActionKind'] = None):
        self.diagnostics = diagnostics
        self.only = only


class CodeActionKindAbstract:
    def __init__(self, value_set: List[str]):
        self.valueSet = value_set


class CodeActionLiteralSupportAbstract:
    def __init__(self, code_action_kind: CodeActionKindAbstract):
        self.codeActionKind = code_action_kind


class CodeActionOptions:
    def __init__(self, code_action_kinds: List[CodeActionKind] = None):
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
                 command: 'Command' = None,
                 data: Any = None):
        self.range = range
        self.command = command
        self.data = data


class CodeLensOptions:
    def __init__(self, resolve_provider: bool = False):
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
                 text_edit: 'TextEdit' = None,
                 additional_text_edits: List['TextEdit'] = None):
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
    def __init__(self, title: str, command: str, arguments: Optional[List[Any]] = None):
        self.title = title
        self.command = command
        self.arguments = arguments


class CompletionContext:
    def __init__(self,
                 trigger_kind: 'CompletionTriggerKind',
                 trigger_character: str = None):
        self.triggerKind = trigger_kind
        self.triggerCharacter = trigger_character


class CompletionItem:
    def __init__(self,
                 label: str,
                 kind: 'CompletionItemKind' = None,
                 detail: str = None,
                 documentation: Union[str, 'MarkupContent'] = None,
                 deprecated: bool = False,
                 preselect: bool = False,
                 sort_text: str = None,
                 filter_text: str = None,
                 insert_text: str = None,
                 insert_text_format: 'InsertTextFormat' = None,
                 text_edit: 'TextEdit' = None,
                 additional_text_edits: List['TextEdit'] = None,
                 commit_characters: List[str] = None,
                 command: Command = None,
                 data: Any = None):
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


class CompletionRegistrationOptions:
    def __init__(self,
                 resolve_provider: bool = False,
                 trigger_characters: List[str] = None):
        self.resolveProvider = resolve_provider
        self.triggerCharacters = trigger_characters


class ConfigurationItem:
    def __init__(self,
                 scope_uri: str = None,
                 section: str = None):
        self.scopeUri = scope_uri
        self.section = section


class ConfigurationParams:
    def __init__(self, items: List[ConfigurationItem]):
        self.items = items


class CreateFile:
    def __init__(self, uri: str, options: Optional['CreateFileOptions'] = None):
        self.kind = 'create'
        self.uri = uri
        self.options = options


class CreateFileOptions:
    def __init__(self,
                 overwrite: Optional[bool] = False,
                 ignore_if_exists: Optional[bool] = False):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class DeleteFile:
    def __init__(self, uri: str, options: Optional['DeleteFileOptions']):
        self.kind = 'delete'
        self.uri = uri
        self.options = options


class DeleteFileOptions:
    def __init__(self,
                 recursive: bool = False,
                 ignore_if_exists: bool = False):
        self.recursive = recursive
        self.ignore_if_exists = ignore_if_exists


class Diagnostic:
    def __init__(self,
                 range: 'Range',
                 message: str,
                 severity: Optional['DiagnosticSeverity'] = None,
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
                 language: Optional[str] = None,
                 scheme: Optional[str] = None,
                 pattern: Optional[str] = None):
        self.language = language
        self.scheme = scheme
        self.pattern = pattern


class DocumentFormattingParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 options: 'FormattingOptions'):
        self.textDocument = text_document
        self.options = options


class DocumentHighlight:
    def __init__(self,
                 range: 'Range',
                 kind: DocumentHighlightKind = DocumentHighlightKind.Text):
        self.range = range
        self.kind = kind


class DocumentLink:
    def __init__(self, range: 'Range', target: str = None, data: Any = None):
        self.range = range
        self.target = target
        self.data = data


class DocumentLinkOptions:
    def __init__(self, resolve_provider: bool = False):
        self.resolveProvider = resolve_provider


class DocumentLinkParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DocumentOnTypeFormattingOptions:
    def __init__(self,
                 first_trigger_character: str,
                 more_trigger_character: List[str] = None):
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
                 detail: str = None,
                 children: List['DocumentSymbol'] = None,
                 deprecated: bool = False):
        self.name = name
        self.kind = kind
        self.range = range
        self.selectionRange = selection_range
        self.detail = detail
        self.children = children
        self.deprecated = deprecated


class DocumentSymbolParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DynamicRegistrationAbstract:
    def __init__(self, dynamic_registration: bool):
        self.dynamicRegistration = dynamic_registration


class ExecuteCommandOptions:
    def __init__(self, commands: List[str]):
        self.commands = commands


c


class FileEvent:
    def __init__(self, uri: str, type: FileChangeType):
        self.uri = uri
        self.type = type


class FileSystemWatcher:
    def __init__(self,
                 glob_pattern: str,
                 kind: _WatchKindType = WatchKind.Create | WatchKind.Change | WatchKind.Delete):
        self.globPattern = glob_pattern
        self.kind = kind


class FoldingRange:
    def __init__(self,
                 start_line: int,
                 start_character: int,
                 end_line: int,
                 end_character: int,
                 kind: 'FoldingRangeKind' = None):
        self.startLine = start_line
        self.startCharacter = start_character
        self.endLine = end_line
        self.endCharacter = end_character
        self.kind = kind


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
    def __init__(self, contents: Any, range: 'Range' = None):
        self.contents = contents
        self.range = range


class ClientInfo:
    def __init__(self, name: str = 'unknown', version: Optional[str] = None):
        self.name = name
        self.version = version


class InitializeParams(WorkDoneProgressParams):
    def __init__(self,
                 process_id: Union[int, None],
                 capabilities: ClientCapabilities,
                 client_info: Optional[ClientInfo] = None,
                 root_uri: Union[str, None] = None,
                 root_path: Optional[str] = None,
                 initialization_options: Optional[Any] = None,
                 trace: Optional[Trace] = Trace.Off,
                 workspace_folders: Optional[List['WorkspaceFolder']] = None,
                 work_done_token: Optional[bool] = None) -> None:
        super().__init__(work_done_token)
        self.processId = process_id
        self.clientInfo = client_info
        self.rootPath = root_path
        self.rootUri = root_uri
        self.initializationOptions = initialization_options
        self.capabilities = capabilities
        self.trace = trace
        self.workspaceFolders = workspace_folders or []


class InitializeResult:
    def __init__(self,
                 capabilities: 'ServerCapabilities',
                 server_info: Optional[ServerInfo] = None):
        self.capabilities = capabilities
        self.serverInfo = server_info


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
                 origin_selection_range: Optional['Range'] = None):
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


class MessageActionItem:
    def __init__(self, title: str):
        self.title = title


class ExecuteCommandParams:
    def __init__(self, command: str, arguments: List[object] = None):
        self.command = command
        self.arguments = arguments


class ExecuteCommandRegistrationOptions:
    def __init__(self, commands: List[str]):
        self.commands = commands


class ParameterInformation:
    def __init__(self,
                 label: str,
                 documentation: Union[str, MarkupContent] = None):
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


class ProgressParams(Generic[T]):
    def __init__(self, token: ProgressToken, value: T):
        self.token = token
        self.value = value


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
    def __init__(self, id: str, method: str, register_options: Any = None):
        self.id = id
        self.method = method
        self.registerOptions = register_options


class RegistrationParams:
    def __init__(self, registrations: List[Registration]):
        self.registrations = registrations


class RenameFile:
    def __init__(self,
                 old_uri: str,
                 new_uri: str,
                 options: Optional['RenameFileOptions'] = None):
        self.kind = 'rename'
        self.oldUri = old_uri
        self.newUri = new_uri
        self.options = options


class RenameFileOptions:
    def __init__(self,
                 overwrite: Optional[bool] = False,
                 ignore_if_exists: Optional[bool] = False):
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


class X(WorkDoneProgressOptions):
    def __init__(self,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


# class ServerCapabilities:
#     def __init__(self,
#                  features,
#                  feature_options,
#                  commands,
#                  sync_kind,
#                  client_capabilities):
#         self.textDocumentSync = sync_kind
#         self.hoverProvider = HOVER in features

#         if COMPLETION in features:
#             self.completionProvider = CompletionOptions(
#                 resolve_provider=COMPLETION_ITEM_RESOLVE in features,
#                 trigger_characters=feature_options.get(
#                     COMPLETION, {}).get('trigger_characters', [])
#             )

#         if SIGNATURE_HELP in features:
#             self.signatureHelpProvider = SignatureHelpOptions(
#                 trigger_characters=feature_options.get(
#                     SIGNATURE_HELP, {}).get('trigger_characters', [])
#             )

#         self.definitionProvider = DEFINITION in features

#         self.referencesProvider = REFERENCES in features
#         self.documentHighlightProvider = DOCUMENT_HIGHLIGHT in features
#         self.documentSymbolProvider = DOCUMENT_SYMBOL in features
#         self.workspaceSymbolProvider = WORKSPACE_SYMBOL in features
#         self.codeActionProvider = CODE_ACTION in features

#         if CODE_LENS in features:
#             self.codeLensProvider = CodeLensOptions(
#                 resolve_provider=CODE_LENS_RESOLVE in features
#             )

#         self.documentFormattingProvider = FORMATTING in features
#         self.documentRangeFormattingProvider = RANGE_FORMATTING in features

#         if FORMATTING in features:
#             self.documentOnTypeFormattingProvider = \
#                 DocumentOnTypeFormattingOptions(
#                     first_trigger_character=feature_options.get(
#                         ON_TYPE_FORMATTING, {})
#                     .get('first_trigger_character', ''),

#                     more_trigger_character=feature_options.get(
#                         ON_TYPE_FORMATTING, {})
#                     .get('more_trigger_character', [])
#                 )

#         self.renameProvider = RENAME in features

#         if DOCUMENT_LINK in features:
#             self.documentLinkProvider = DocumentLinkOptions(
#                 resolve_provider=DOCUMENT_LINK_RESOLVE in features
#             )

#         self.executeCommandProvider = ExecuteCommandOptions(
#             commands=list(commands.keys())
#         )

#         self.workspace = {
#             'workspaceFolders': {
#                 'supported': True,
#                 'changeNotifications': True
#             }
#         }

#     def __repr__(self):
#         return '{}( {} )'.format(type(self).__name__, self.__dict__)


class SelectionRangeClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class ShowMessageParams:
    def __init__(self, type: MessageType, message: str):
        self.type = type
        self.message = message


class ShowMessageRequestParams:
    def __init__(self,
                 type: MessageType,
                 message: str,
                 actions: List[MessageActionItem]):
        self.type = type
        self.message = message
        self.actions = actions


class SignatureHelp:
    def __init__(self,
                 signatures: List['SignatureInformation'],
                 active_signature: int = 0,
                 active_parameter: int = 0):
        self.signatures = signatures
        self.activeSignature = active_signature
        self.activeParameter = active_parameter


class SignatureInformation:
    def __init__(self,
                 label: str,
                 documentation: Union[str, MarkupContent] = None,
                 parameters: List[ParameterInformation] = None):
        self.label = label
        self.documentation = documentation
        self.parameters = parameters


class SignatureInformationAbstract:
    def __init__(self, documentation_format: List[MarkupKind]):
        self.documentationFormat = documentation_format


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
                 container_name: str = None,
                 deprecated: bool = False):
        self.name = name
        self.kind = kind
        self.location = location
        self.containerName = container_name
        self.deprecated = deprecated


class TextDocumentContentChangeEvent:
    def __init__(self,
                 range: 'Range',
                 range_length: Optional[NumType] = None,
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
    def __init__(self, uri: str, version: Union[NumType, None]):
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
                 context: CompletionContext):
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


class DocumentOnTypeFormattingRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 first_trigger_character: str = None,
                 more_trigger_characters: List[str] = None):
        super().__init__(document_selector)
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_characters


class RenameRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 prepare_provider: bool = False):
        super().__init__(document_selector)
        self.prepareProvider = prepare_provider


class ServerInfo:
    def __init__(self, name: str = 'unknown', version: Optional[str] = None):
        self.name = name
        self.version = version


class SignatureHelpRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 trigger_characters: List[str] = None):
        super().__init__(document_selector)
        self.triggerCharacters = trigger_characters


class TextDocumentSaveRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 include_text: bool = False):
        super().__init__(document_selector)
        self.includeText = include_text


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


class WorkspaceEdit:
    def __init__(self,
                 changes: Optional[Dict[str, List[TextEdit]]] = None,
                 document_changes: Optional[DocumentChangesType] = None):
        self.changes = changes
        self.documentChanges = document_changes


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
