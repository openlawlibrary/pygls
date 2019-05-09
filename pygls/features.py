############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
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
"""This module contains all features supported by Language Server Protocol

LSP Specification:
    https://microsoft.github.io/language-server-protocol/specification
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
DECLARATION = 'textDocument/declaration'
DEFINITION = 'textDocument/definition'
DOCUMENT_COLOR = 'textDocument/documentColor'
DOCUMENT_HIGHLIGHT = 'textDocument/documentHighlight'
DOCUMENT_LINK = 'textDocument/documentLink'
DOCUMENT_LINK_RESOLVE = 'documentLink/resolve'
DOCUMENT_SYMBOL = 'textDocument/documentSymbol'
FOLDING_RANGE = 'textDocument/foldingRange'
FORMATTING = 'textDocument/formatting'
HOVER = 'textDocument/hover'
IMPLEMENTATION = 'textDocument/implementation'
ON_TYPE_FORMATTING = 'textDocument/onTypeFormatting'
PREPARE_RENAME = 'textDocument/prepareRename'
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
