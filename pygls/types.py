##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
from typing import Any, Dict, List, Optional, Union

from .features import (CODE_ACTION, CODE_LENS, CODE_LENS_RESOLVE, COMPLETION,
                       COMPLETION_ITEM_RESOLVE, DEFINITION, DOCUMENT_HIGHLIGHT,
                       DOCUMENT_LINK, DOCUMENT_LINK_RESOLVE, DOCUMENT_SYMBOL,
                       FORMATTING, HOVER, ON_TYPE_FORMATTING, RANGE_FORMATTING,
                       REFERENCES, RENAME, SIGNATURE_HELP, WORKSPACE_SYMBOL)

"""
This module contains Language Server Protocol constants
https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md
"""


# Classes used for type hints.
DocumentChangesType = Union[List['TextDocumentEdit'],
                            'TextDocumentEdit',
                            'CreateFile', 'RenameFile', 'DeleteFile']
DocumentSelectorType = List['DocumentFilter']
NumType = Union[int, float]


class ApplyWorkspaceEditParams:
    def __init__(self, edit: 'WorkspaceEditCapability', label: Optional[str]):
        self.edit = edit
        self.label = label


class ApplyWorkspaceEditResponse:
    def __init__(self, applied: bool):
        self.applied = applied


class ClientCapabilities:
    def __init__(self,
                 workspace: 'WorkspaceClientCapabilities',
                 text_document: 'TextDocumentClientCapabilities',
                 experimental: Any):
        self.workspace = workspace
        self.textDocument = text_document
        self.experimental = experimental


class CodeActionAbstract:
    def __init(self,
               dynamic_registration: bool,
               code_action_literal_support:
               'CodeActionLiteralSupportAbstract'):
        self.dynamicRegistration = dynamic_registration
        self.codeActionLiteralSupport = code_action_literal_support


class CodeActionKind:
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
    def __init__(self, code_action_kinds: List[CodeActionKind] = None):
        self.codeActionKinds = code_action_kinds


class CodeLensOptions:
    def __init__(self, resolve_provider):
        self.resolveProvider = resolve_provider


class ColorProviderOptions:
    pass


class Command:
    def __init__(self, title: str, command: str, arguments: List[Any] = None):
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
                 trigger_character: str = None):
        self.triggerKind = trigger_kind
        self.triggerCharacter = trigger_character


class CompletionItem:
    def __init__(self,
                 label,
                 kind=None,
                 detail=None,
                 documentation=None,

                 deprecated=None,
                 preselect=None,
                 sort_text=None,
                 filter_text=None,
                 insert_text=None,
                 insert_text_format=None,
                 text_edit=None,
                 additional_text_edits=None,
                 commit_characters=None,
                 command=None,
                 data=None):
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


class CompletionItemKind:
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
    def __init__(self, is_incomplete, items=None):
        self.isIncomplete = is_incomplete
        self.items = items if items else []

    def add_item(self, completion_item):
        self.items.append(completion_item)

    def add_items(self, completion_items):
        self.items.extend(completion_items)


class CompletionOptions:
    def __init__(self, resolve_provider=None, trigger_characters=None):
        self.resolveProvider = resolve_provider
        self.triggerCharacters = trigger_characters


class CompletionRegistrationOptions:
    def __init__(self,
                 trigger_characters: List[str] = None,
                 resolve_provider: bool = False):
        self.triggerCharacters = trigger_characters
        self.resolveProvider = resolve_provider


class CompletionTriggerKind:
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3


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
    def __init__(self, uri: str, options: 'CreateFileOptions' = None):
        self.kind = 'create'
        self.uri = uri
        self.options = options


class CreateFileOptions:
    def __init__(self,
                 overwrite: bool = False,
                 ignore_if_exists: bool = False):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class DeleteFile:
    def __init__(self, uri: str, options: 'DeleteFileOptions'):
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
    def __init__(
        self,
        range: 'Range',
        message: str,
        severity: 'DiagnosticSeverity' = 1,
        code: str = None,
        source: str = None,
        related_information: 'DiagnosticRelatedInformation' = None
    ):
        self.range = range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source
        self.relatedInformation = related_information


class DiagnosticSeverity:
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


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
    def __init__(self, events: 'WorkspaceFoldersChangeEvent'):
        self.events = events


class DidCloseTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DidOpenTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentIdentifier'):
        self.textDocument = text_document


class DidSaveTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentIdentifier', text: str):
        self.textDocument = text_document
        self.text = text


class DocumentFilter:
    def __init__(self,
                 language: str = None,
                 scheme: str = None,
                 pattern: str = None):
        self.language = language
        self.scheme = scheme
        self.pattern = pattern


class DocumentHighlightKind:
    Text = 1
    Read = 2
    Write = 3


class DocumentLinkOptions:
    def __init__(self, resolve_provider):
        self.resolveProvider = resolve_provider


class DocumentOnTypeFormattingOptions:
    def __init__(self, first_trigger_character, more_trigger_character):
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_character


class DocumentSymbol:
    def __init__(self,
                 dynamic_registration: bool,
                 symbol_kind: 'SymbolKindAbstract',
                 hierarchical_document_symbol_support: bool):
        self.dynamicRegistration = dynamic_registration,
        self.symbolKind = symbol_kind
        self.hierarchicalDocumentSymbolSupport = \
            hierarchical_document_symbol_support


class DynamicRegistrationAbstract:
    def __init__(self, dynamic_registration: bool):
        self.dynamicRegistration = dynamic_registration


class ExecuteCommandOptions:
    def __init__(self, commands):
        self.commands = commands


class FailureHandlingKind:
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    FailureHandlingKind = 'undo'


class FileChangeType:
    Created = 1
    Changed = 2
    Deleted = 3


class FileEvent:
    def __init__(self, uri: str, type: FileChangeType):
        self.uri = uri
        self.type = type


class FileSystemWatcher:
    def __init__(self, glob_pattern: str, kind: int = 7):
        self.globPattern = glob_pattern
        self.kind = kind


class FoldingRangeAbstract:
    def __init(self,
               dynamic_registration: bool,
               range_limit: NumType,
               line_folding_only: bool):
        self.dynamicRegistration = dynamic_registration
        self.rangeLimit = range_limit
        self.lineFoldingOnly = line_folding_only


class Hover:
    def __init__(self, contents: Any, range: 'Range' = None):
        self.contents = contents
        self.range = range


class HoverAbstract:
    def __init__(self, dynamic_registration,
                 content_format: List['MarkupKindEnum']):
        self.dynamicRegistration = dynamic_registration
        self.contentFormat = content_format


class InitializeParams:
    def __init__(self,
                 process_id: int = None,
                 root_path: str = None,
                 root_uri: str = None,
                 initialization_options: Any = None,
                 capabilities: ClientCapabilities = None,
                 trace: 'Trace' = 'off',
                 workspace_folders: List['WorkspaceFolder'] = None):
        self.processId = process_id
        self.rootPath = root_path
        self.rootUri = root_uri
        self.initializationOptions = initialization_options
        self.capabilities = capabilities
        self.trace = trace
        self.workspaceFolders = workspace_folders


class InitializeResult:
    def __init__(self, capabilities: 'ServerCapabilities'):
        self.capabilities = capabilities


class InsertTextFormat:
    PlainText = 1
    Snippet = 2


class Location:
    def __init__(self, uri: str, range: 'Range'):
        self.uri = uri
        self.range = range


class LogMessageParams:
    def __init__(self, type: NumType, message: str):
        self.type = type
        self.message = message


class MarkupContent:
    def __init__(self, kind: 'MarkupKind', value: str):
        self.kind = kind
        self.value = value


class MarkupKind:
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MessageActionItem:
    def __init__(self, title: str):
        self.title = title


class MessageType:
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


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
        if self.line == other.line and self.character == other.character:
            return True
        return False

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

    def __repr__(self):
        return '{}:{}'.format(self.line, self.character)


class PublishDiagnosticsAbstract:
    def __init(self, related_information: bool):
        self.relatedInformation = related_information


class PublishDiagnosticsParams:
    def __init__(self, uri: str, diagnostics: List[Diagnostic]):
        self.uri = uri
        self.diagnostics = diagnostics


class Range:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end


class Registration:
    def __init__(self, id: str, method: str, register_options: Any = None):
        self.id = id
        self.method = method
        self.registerOptions = register_options


class RegistrationOptions:
    def __init__(self, registrations: List[Registration]):
        self.registrations = registrations


class RenameAbstract:
    def __init(self, dynamic_registration: bool, prepare_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.prepareSupport = prepare_support


class RenameFile:
    def __init__(self,
                 old_uri: str,
                 new_uri: str,
                 options: 'RenameFileOptions' = None):
        self.kind = 'rename'
        self.old_uri = old_uri
        self.new_uri = new_uri
        self.options = options


class RenameFileOptions:
    def __init__(self,
                 overwrite: bool = False,
                 ignore_if_exists: bool = False):
        self.overwrite = overwrite
        self.ignoreIfExists = ignore_if_exists


class ResourceOperationKind:
    Create = 'create'
    Rename = 'rename'
    Delete = 'delete'


class SaveOptions:
    def __init__(self, include_text):
        self.includeText = include_text


class ServerCapabilities:
    def __init__(
        self,
        features,
        feature_options,
        commands,
        client_capabilities
    ):
        self.textDocumentSync = TextDocumentSyncKind.INCREMENTAL
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

        # Additional options
        # self.typeDefinitionProvider = False
        # self.implementationProvider = False

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

        # self.colorProvider = False

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
        self.activeSignature = active_parameter
        self.activeParameter = active_parameter


class SignatureHelpAbstract:
    def __init__(self, dynamic_registration,
                 signature_information: List[MarkupKind]):
        self.dynamicRegistration = dynamic_registration
        self.signatureInformation = signature_information


class SignatureHelpOptions:
    def __init__(self, trigger_characters):
        self.triggerCharacters = trigger_characters


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


class StaticRegistrationOptions:
    def __init__(self, id):
        self.id = id


class SymbolAbstract:
    def __init__(self,
                 dynamic_registration: bool,
                 symbol_kind: 'SymbolKindAbstract'):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind


class SymbolKind:
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
    NumTypeber = 16
    Boolean = 17
    Array = 18


class SymbolKindAbstract:
    def __init__(self, value_set: SymbolKind):
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
                 document_symbol: DocumentSymbol,
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
        self.formatting = formatting
        self.rangeFormatting = range_formatting
        self.onTypeFormatting = on_type_formatting
        self.definition = definition
        self.typeDefinition = type_definition
        self.implementation = implementation
        self.codeAction = code_action
        self.codeLens = code_lens
        self.documentLink = document_highlight
        self.colorProvider = color_provider
        self.rename = rename
        self.publishDiagnostics = publish_diagnostics
        self.foldingRange = folding_range


class TextDocumentContentChangeEvent:
    def __init__(self, range: 'Range', range_length: NumType, text: str):
        self.range = range
        self.range_length = range_length
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


class TextDocumentPositionParams:
    def __init__(self,
                 text_document: 'TextDocumentIdentifier',
                 position: Position):
        self.textDocument = text_document
        self.position = position


class CompletionParams(TextDocumentPositionParams):
    def __init__(self, context: CompletionContext):
        self.context = context


class TextDocumentRegistrationOptions:
    def __init__(self, document_selector: DocumentSelectorType = None):
        self.documentSelector = document_selector


class TextDocumentSaveReason:
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class SignatureHelpRegistrationOptions(TextDocumentRegistrationOptions):
    def __init(self, trigger_characters: List[str] = None):
        self.triggerCharacters = trigger_characters


class TextDocumentSaveRegistrationOptions(TextDocumentRegistrationOptions):
    def __init__(self,
                 document_selector: DocumentSelectorType = None,
                 include_text: bool = False):
        super.__init__(document_selector)
        self.includeText = include_text


class TextDocumentSyncOptions:
    def __init__(self,
                 open_close,
                 change,
                 will_save,
                 will_save_wait_until,
                 save):
        self.openClose = open_close
        self.change = change
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.save = save


class TextDocumentSyncKind:
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class TextEdit:
    def __init__(self, range: Range, new_text: str):
        self.range = range
        self.newText = new_text


class Trace:
    Off = 'off'
    Messages = 'messages'
    Verbose = 'verbose'


class Unregistration:
    def __init__(self, id: str, method: str):
        self.id = id
        self.method = method


class UnregistrationParams:
    def __init__(self, unregistrations: List[Unregistration]):
        self.unregistration = unregistrations


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    def __init__(self, uri: str, version: NumType):
        super().__init__(uri)
        self.version = version


class WatchKind:
    Create = 1
    Change = 2
    Delete = 4


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
                 changes: Dict[str, List[TextEdit]] = None,
                 document_changes: DocumentChangesType = None):
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
