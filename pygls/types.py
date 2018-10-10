##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
from typing import List, Optional, Union
'''
Some Language Server Protocol constants
https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md
'''

'''
Classes used for type hints.
'''
Num = Union[int, float]


class _CodeAction:
    def __init(self, dynamic_registration: bool,
               code_action_literal_support: '_CodeActionLiteralSupport'):
        self.dynamicRegistration = dynamic_registration
        self.codeActionLiteralSupport = code_action_literal_support


class _CodeActionKind:
    def __init__(self, value_set: List['CodeActionKind']):
        self.valueSet = value_set


class _CodeActionLiteralSupport:
    def __init__(self, code_action_kind: _CodeActionKind):
        self.codeActionKind = code_action_kind


class _FoldingRange:
    def __init(self, dynamic_registration: bool, range_limit: Num,
               line_folding_only: bool):
        self.dynamicRegistration = dynamic_registration
        self.rangeLimit = range_limit
        self.lineFoldingOnly = line_folding_only


class _Completion:
    def __init__(self, dynamic_registration: bool,
                 completion_item: '_CompletionItem',
                 completion_item_kind: '_CompletionItemKind',
                 context_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.completionItem = completion_item
        self.completionItemKind = completion_item_kind
        self.contextSupport = context_support


class _CompletionItem:
    def __init__(self, snippet_support: bool, commit_character_support: bool,
                 documentation_format: List['MarkupKind'],
                 deprecated_support: bool, preselected_support):
        self.snippetSupport = snippet_support
        self.commitCharacterSupport = commit_character_support
        self.documentationFormat = documentation_format
        self.deprecatedSupport = deprecated_support
        self.preselectedSupport = preselected_support


class _CompletionItemKind:
    def __init__(self, value_set: List['CompletionItemKind']):
        self.valueSet = value_set


class DocumentSymbol:
    def __init__(self, dynamic_registration: bool, symbol_kind: '_SymbolKind',
                 hierarchical_document_symbol_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind
        self.hierarchicalDocumentSymbolSupport = \
            hierarchical_document_symbol_support


class _DynamicRegistration:
    def __init__(self, dynamic_registration: bool):
        self.dynamicRegistration = dynamic_registration


class _Hover:
    def __init__(self, dynamic_registration,
                 content_format: List['MarkupKind']):
        self.dynamicRegistration = dynamic_registration
        self.contentFormat = content_format


class _PublishDiagnostics:
    def __init(self, related_information: bool):
        self.relatedInformation = related_information


class _Rename:
    def __init(self, dynamic_registration: bool, prepare_support: bool):
        self.dynamicRegistration = dynamic_registration
        self.prepareSupport = prepare_support


class _SignatureHelp:
    def __init__(self, dynamic_registration,
                 signature_information: List['MarkupKind']):
        self.dynamicRegistration = dynamic_registration
        self.signatureInformation = signature_information


class _SignatureInformation:
    def __init__(self, documentation_format: List['MarkupKind']):
        self.documentationFormat = documentation_format


class _Symbol:
    def __init__(self, dynamic_registration: bool,
                 symbol_kind: '_SymbolKind'):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind


class _SymbolKind:
    def __init__(self, value_set: 'SymbolKind'):
        self.valueSet = value_set


class _Synchronization:
    def __init__(self, dynamic_registration: bool, will_save: bool,
                 will_save_wait_until: bool, did_save: bool):
        self.dynamicRegistration = dynamic_registration
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.didSave = did_save


class _TextDocumentContentChangeEvent:
    def __init__(self, range: 'Range', range_length: Num, text: str):
        self.range = range
        self.range_length = range_length
        self.text = text


class _TextDocumentIdentifier:
    def __init__(self, uri: str):
        self.uri = uri


class _VersionedTextDocumentIdentifier(_TextDocumentIdentifier):
    def __init__(self, uri: str, version: Num):
        super().__init__(uri)
        self.version = version


class _WorkspaceFoldersChangeEvent:
    def __init__(self,
                 added: List['WorkspaceFolder'],
                 removed: List['WorkspaceFolder']):
        self.added = added
        self.removed = removed


'''
Methods
'''

# Client
CLIENT_REGISTER_CAPABILITY = 'client/registerCapability'
CLIENT_UNREGISTER_CAPABILITY = 'client/unregisterCapability'

# Diagnostics
TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'

# General
EXIT = 'exit'
INITIALIZE = 'initialize'
INITIALIZED = 'initialized'
SHUTDOWN = 'shutdown'

# Language Features
CODE_ACTION = 'textDocument/codeAction'
CODE_LENS = 'textDocument/codeLens'
CODE_LENS_RESOLVE = 'codeLens/resolve'
COLOR_PRESENTATION = 'textDocument/colorPresentation'
COMPLETION = 'textDocument/completion'
COMPLETION_ITEM_RESOLVE = 'completionItem/resolve'
DEFINITION = 'textDocument/definition'
DOCUMENT_HIGHLIGHT = 'textDocument/documentHighlight'
DOCUMENT_LINK = 'textDocument/documentLink'
DOCUMENT_LINK_RESOLVE = 'documentLink/resolve'
DOCUMENT_SYMBOL = 'textDocument/documentSymbol'
FORMATTING = 'textDocument/formatting'
HOVER = 'textDocument/hover'
IMPLEMENTATION = 'textDocument/implementation'
ON_TYPE_FORMATTING = 'textDocument/onTypeFormatting'
RANGE_FORMATTING = 'textDocument/rangeFormatting'
REFERENCES = 'textDocument/references'
RENAME = 'textDocument/rename'
SIGNATURE_HELP = 'textDocument/signatureHelp'
TYPE_DEFINITION = 'textDocument/typeDefinition'

# Telemetry
TELEMETRY_EVENT = 'telemetry/event'

# Text Synchronization
TEXT_DOCUMENT_DID_CHANGE = 'textDocument/didChange'
TEXT_DOCUMENT_DID_CLOSE = 'textDocument/didClose'
TEXT_DOCUMENT_DID_OPEN = 'textDocument/didOpen'
TEXT_DOCUMENT_DID_SAVE = 'textDocument/didSave'
TEXT_DOCUMENT_WILL_SAVE = 'textDocument/willSave'
TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL = 'textDocument/willSaveWaitUntil'

# Window
WINDOW_LOG_MESSAGE = 'window/logMessage'
WINDOW_SHOW_MESSAGE = 'window/showMessage'
WINDOW_SHOW_MESSAGE_REQUEST = 'window/showMessageRequest'

# Workspace
WORKSPACE_APPLY_EDIT = 'workspace/applyEdit'
WORKSPACE_CONFIGURATION = 'workspace/configuration'
WORKSPACE_DID_CHANGE_CONFIGURATION = 'workspace/didChangeConfiguration'
WORKSPACE_DID_CHANGE_WATCHED_FILES = 'workspace/didChangeWatchedFiles'
WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS = 'workspace/didChangeWorkspaceFolders'
WORKSPACE_EXECUTE_COMMAND = 'workspace/executeCommand'
WORKSPACE_FOLDERS = 'workspace/folders'
WORKSPACE_SYMBOL = 'workspace/symbol'

'''
Language Server Protocol classes
'''


class ClientCapabilities:
    def __init__(self, workspace: 'WorkspaceClientCapabilities',
                 text_document: 'TextDocumentClientCapabilities',
                 experimental: object):
        self.workspace = workspace
        self.textDocument = text_document
        self.experimental = experimental


class CodeLensOptions:
    def __init__(self, resolve_provider):
        self.resolveProvider = resolve_provider


class ColorProviderOptions:
    pass


class Command:
    def __init__(self, title, command, arguments=None):
        self.title = title
        self.command = command
        self.arguments = arguments


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


class CompletionList:
    def __init__(self, is_incomplete, items=None):
        self.isIncomplete = is_incomplete
        self.items = items if items else []

    def add_item(self, completion_item):
        self.items.append(completion_item)

    def add_items(self, completion_items):
        self.items.extend(completion_items)


class CompletionItem:
    def __init__(self, label, kind=None, detail=None, documentation=None,
                 deprecated=None, preselect=None, sort_text=None,
                 filter_text=None, insert_text=None, insert_text_format=None,
                 text_edit=None, additional_text_edits=None,
                 commit_characters=None, command=None, data=None):
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


class CompletionOptions:
    def __init__(self, resolve_provider=None, trigger_characters=None):
        self.resolveProvider = resolve_provider
        self.triggerCharacters = trigger_characters


class ConfigurationItem:
    def __init__(self,
                 scope_uri: Optional[str] = None,
                 section: Optional[str] = None):
        self.scopeUri = scope_uri
        self.section = section


class ConfigurationParams:
    def __init__(self, items: List[ConfigurationItem]):
        self.items = items


class DiagnosticSeverity:
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class Diagnostic:
    def __init__(
        self,
        range,
        message,
        severity=DiagnosticSeverity.Error,
        code=None,
        source=None,
        related_information=None
    ):
        self.range = range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source
        self.relatedInformation = related_information


class DiagnosticRelatedInformation:
    def __init__(self, location, message):
        self.location = location
        self.message = message


class DidOpenTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentItem'):
        self.textDocument = text_document


class DidChangeTextDocumentParams:
    def __init__(self, text_document: _VersionedTextDocumentIdentifier,
                 content_changes: List[_TextDocumentContentChangeEvent]):
        self.textDocument = text_document
        self.contentChanges = content_changes


class DidChangeWorkspaceFoldersParams:
    def __init__(self, events: _WorkspaceFoldersChangeEvent):
        self.events = events


class DidCloseTextDocumentParams:
    def __init__(self, text_document: 'TextDocumentItem'):
        self.textDocument = text_document


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


class ExecuteCommandOptions:
    def __init__(self, commands):
        self.commands = commands


class FailureHandlingKind:
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    FailureHandlingKind = 'undo'


class InitializeParams:
    def __init__(self, process_id: int, root_path: str, root_uri: str,
                 initialization_options: object,
                 capabilities: ClientCapabilities):
        self.processId = None
        self.rootPath = None
        self.rootUri = None
        self.initializationOptions = {}
        self.capabilities = None
        self.trace = None
        self.workspaceFolders = None


class InitializeResult:
    def __init__(self, capabilities: 'ServerCapabilities'):
        self.capabilities = capabilities


class InsertTextFormat:
    PlainText = 1
    Snippet = 2


class Location:
    def __init__(self, uri, range):
        self.uri = uri
        self.range = range


class MarkupKind:
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MessageType:
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class ExecuteCommandParams:
    def __init__(self, command: str, arguments: List[object] = None):
        self.command = command
        self.arguments = arguments


class Position:
    def __init__(self, line=0, character=0):
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


class PublishDiagnosticsParams:
    def __init__(self, uri, diagnostics):
        self.uri = uri
        self.diagnostics = diagnostics


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end


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


class SignatureHelpOptions:
    def __init__(self, trigger_characters):
        self.triggerCharacters = trigger_characters


class StaticRegistrationOptions:
    def __init__(self, id):
        self.id = id


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
    Number = 16
    Boolean = 17
    Array = 18


class TextDocumentClientCapabilities:

    def __init__(self,
                 synchronization: _Synchronization,
                 completion: _Completion,
                 hover: _Hover,
                 signature_help: _SignatureHelp,
                 references: _DynamicRegistration,
                 document_highlight: _DynamicRegistration,
                 document_symbol: DocumentSymbol,
                 formatting: _DynamicRegistration,
                 range_formatting: _DynamicRegistration,
                 on_type_formatting: _DynamicRegistration,
                 definition: _DynamicRegistration,
                 type_definition: _DynamicRegistration,
                 implementation: _DynamicRegistration,
                 code_action: _CodeAction,
                 code_lens: _DynamicRegistration,
                 document_link: _DynamicRegistration,
                 color_provider: _DynamicRegistration,
                 rename: _Rename,
                 publish_diagnostics: _PublishDiagnostics,
                 folding_range: _FoldingRange):
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


class TextDocumentItem:
    def __init__(self, uri: str, language_id: str, version: Num, text: str):
        self.uri = uri
        self.languageId = language_id
        self.version = version
        self.text = text


class TextDocumentSyncKind:
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class TextDocumentSyncOptions:
    def __init__(self, open_close, change, will_save, will_save_wait_until,
                 save):
        self.openClose = open_close
        self.change = change
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.save = save


class TextEdit:
    def __init__(self, range, new_text):
        self.range = range
        self.newText = new_text


class WorkspaceClientCapabilities:
    def __init__(self, apply_edit: bool, workspace_edit: 'WorkspaceEdit',
                 did_change_configuration: _DynamicRegistration,
                 did_change_watched_files: _DynamicRegistration,
                 symbol: _Symbol, execute_command: _DynamicRegistration,
                 workspace_folders: bool, configuration: bool):
        self.applyEdit = apply_edit
        self.workspaceEdit = workspace_edit
        self.didChangeConfiguration = did_change_configuration
        self.didChangeWatched = did_change_watched_files
        self.symbol = symbol
        self.executeCommand = execute_command
        self.workspace_folders = workspace_folders
        self.configuration = configuration


class WorkspaceEdit:
    def __init__(self, document_changes: bool,
                 resource_operations: List[ResourceOperationKind],
                 failure_handling: FailureHandlingKind):
        self.documentChanges = document_changes
        self.resourceOperations = resource_operations
        self.failureHandling = failure_handling


class WorkspaceFolder:
    def __init__(self, uri: str, name: str):
        self.uri = uri
        self.name = name
