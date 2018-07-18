##########################################################################
# Original work Copyright 2017 Palantir Technologies, Inc.               #
# Original work licensed under the MIT License.                          #
# See ThirdPartyNotices.txt in the project root for license information. #
# All modifications Copyright (c) Open Law Library. All rights reserved. #
##########################################################################
"""
Some Language Server Protocol constants
https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md
"""

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


class CodeLensOptions(object):

    def __init__(self, resolveProvider):
        self.resolveProvider = resolveProvider


class ColorProviderOptions(object):
    pass


class CompletionItemKind(object):
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


class CompletionOptions(object):

    def __init__(self, resolveProvider=None, triggerCharacters=None):
        self.resolveProvider = resolveProvider
        self.triggerCharacters = triggerCharacters


class DiagnosticSeverity(object):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class Diagnostic:
    """Provides a VS Code compatible Diagnostic object. See [1] for details.
        [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#Diagnostic
    """

    def __init__(
        self,
        range,
        message,
        severity=DiagnosticSeverity.Error,
        code=None,
        source=None,
        relatedInformation=None
    ):
        self.range = range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source
        self.relatedInformation = relatedInformation


class DiagnosticRelatedInformation:
    """Provides a VS Code compatible Diagnostic object. See [1] for details.
        [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#DiagnosticRelatedInformation
    """

    def __init__(self, location, message):
        self.location = location
        self.message = message


class DocumentHighlightKind(object):
    Text = 1
    Read = 2
    Write = 3


class DocumentLinkOptions(object):

    def __init__(self, resolveProvider):
        self.resolveProvider = resolveProvider


class DocumentOnTypeFormattingOptions(object):

    def __init__(self, firstTriggerCharacter, moreTriggerCharacter):
        self.firstTriggerCharacter = firstTriggerCharacter
        self.moreTriggerCharacter = moreTriggerCharacter


class ExecuteCommandOptions(object):

    def __init__(self, commands):
        self.commands = commands


class Location:
    """Provides a VS Code compatible Diagnostic object. See [1] for details.
        [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#Location
    """

    def __init__(self, uri, range):
        self.uri = uri
        self.range = range


class MessageType(object):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class Position:
    """Zero-based line and character positions intended to work with VS Code.
        See [1] for details.
        [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#Position
    """

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


class PublishDiagnosticsParams():
    def __init__(self, uri, diagnostics):
        self.uri = uri
        self.diagnostics = diagnostics


class Range:
    """Provides an object to be converted to a VS Code Range object for a given
       document. See [1] for details.
       [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#Range
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end


class SaveOptions(object):

    def __init__(self, includeText):
        self.includeText = includeText


class ServerCapabilities(object):

    def __init__(self, ls):
        features = ls.features.keys()
        feature_options = ls.feature_options
        commands = ls.commands

        self.textDocumentSync = TextDocumentSyncKind.INCREMENTAL
        self.hoverProvider = HOVER in features

        if COMPLETION in features:
            self.completionProvider = CompletionOptions(
                resolveProvider=COMPLETION_ITEM_RESOLVE in features,
                triggerCharacters=feature_options.get(
                    COMPLETION, {}).get('triggerCharacters', [])
            )

        if SIGNATURE_HELP in features:
            self.signatureHelpProvider = SignatureHelpOptions(
                triggerCharacters=feature_options.get(
                    SIGNATURE_HELP, {}).get('triggerCharacters', [])
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
                resolveProvider=CODE_LENS_RESOLVE in features
            )

        self.documentFormattingProvider = FORMATTING in features
        self.documentRangeFormattingProvider = RANGE_FORMATTING in features

        if FORMATTING in features:
            self.documentOnTypeFormattingProvider = \
                DocumentOnTypeFormattingOptions(
                    firstTriggerCharacter=feature_options.get(
                        ON_TYPE_FORMATTING, {})
                    .get('firstTriggerCharacter', ''),

                    moreTriggerCharacter=feature_options.get(
                        ON_TYPE_FORMATTING, {})
                    .get('moreTriggerCharacter', [])
                )

        self.renameProvider = RENAME in features

        if DOCUMENT_LINK in features:
            self.documentLinkProvider = DocumentLinkOptions(
                resolveProvider=DOCUMENT_LINK_RESOLVE in features
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
        return f'{type(self).__name__}( {self.__dict__} )'


class SignatureHelpOptions(object):

    def __init__(self, triggerCharacters):
        self.triggerCharacters = triggerCharacters


class StaticRegistrationOptions(object):

    def __init__(self, id):
        self.id = id


class SymbolKind(object):
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


class TextDocumentSyncKind(object):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class TextDocumentSyncOptions(object):

    def __init__(self, openClose, change, willSave, willSaveWaitUntil, save):
        self.openClose = openClose
        self.change = change
        self.willSave = willSave
        self.willSaveWaitUntil = willSaveWaitUntil
        self.save = save


class TextEdit:
    """Provides a VS Code compatible TextEdit object. See [1] for details.
       [1]: https://code.visualstudio.com/docs/extensionAPI/vscode-api#TextEdit
    """

    def __init__(self, range, newText):
        self.range = range
        self.newText = newText
