# Copyright 2017 Palantir Technologies, Inc.
"""Some Language Server Protocol constants

https://github.com/Microsoft/language-server-protocol/blob/master/protocol.md
"""

# General
INITIALIZE = 'initialize'
INITIALIZED = 'initialized'
SHUTDOWN = 'shutdown'
EXIT = 'exit'

# Window
SHOW_MESSAGE = 'window/showMessage'
SHOW_MESSAGE_REQUEST = 'window/showMessageRequest'
LOG_MESSAGE = 'window/logMessage'

# Telemetry
TELEMETRY_EVENT = 'telemetry/event'

# Client
REGISTER_CAPABILITY = 'client/registerCapability'
UNREGISTER_CAPABILITY = 'client/unregisterCapability'

# Workspace
WORKSPACE_FOLDERS = 'workspace/folders'
DID_CHANGE_WORKSPACE_FOLDERS = 'workspace/didChangeWorkspaceFolders'
DID_CHANGE_CONFIGURATION = 'workspace/didChangeConfiguration'
CONFIGURATION = 'workspace/configuration'
DID_CHANGE_WATCHED_FILES = 'workspace/didChangeWatchedFiles'
SYMBOL = 'workspace/symbol'
EXECUTE_COMMAND = 'workspace/executeCommand'
APPLY_EDIT = 'workspace/applyEdit'

REGISTER_COMMAND = 'registerCommand'

# Text Synchronization
TEXT_DOC_DID_OPEN = 'textDocument/didOpen'
TEXT_DOC_DID_CHANGE = 'textDocument/didChange'
TEXT_DOC_WILL_SAVE = 'textDocument/willSave'
TEXT_DOC_WILL_SAVE_WAIT_UNTIL = 'textDocument/willSaveWaitUntil'
TEXT_DOC_DID_SAVE = 'textDocument/didSave'
TEXT_DOC_DID_CLOSE = 'textDocument/didClose'

# Diagnostics
TEXT_DOC_PUBLISH_DIAGNOSTICS = 'textDocument/publishDiagnostics'

# Language Features
COMPLETION = 'textDocument/completion'
COMPLETION_RESOLVE = 'completionItem/resolve'
HOVER = 'textDocument/hover'
CODE_ACTION = 'textDocument/codeAction'


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


class DocumentHighlightKind(object):
    Text = 1
    Read = 2
    Write = 3


class DiagnosticSeverity(object):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class MessageType(object):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


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
