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

-- General Messages --

Class attributes are named with camel-case notation because client is expecting
that.
"""
import enum
from typing import Any, List, Optional, Union

from pygls.types.basic_structures import (
    NumType,
    WorkDoneProgressParams,
    WorkspaceEditClientCapabilities
)
from pygls.types.diagnostics import PublishDiagnosticsClientCapabilities
from pygls.types.language_features.code_action import (
    CodeActionClientCapabilities,
    CodeActionOptions
)
from pygls.types.language_features.code_lens import (
    CodeLensClientCapabilities,
    CodeLensOptions
)
from pygls.types.language_features.completion import (
    CompletionClientCapabilities,
    CompletionOptions
)
from pygls.types.language_features.declaration import (
    DeclarationClientCapabilities,
    DeclarationOptions,
    DeclarationRegistrationOptions
)
from pygls.types.language_features.definition import (
    DefinitionClientCapabilities,
    DefinitionOptions
)
from pygls.types.language_features.document_color import (
    DocumentColorClientCapabilities,
    DocumentColorOptions,
    DocumentColorRegistrationOptions
)
from pygls.types.language_features.document_highlight import (
    DocumentHighlightClientCapabilities,
    DocumentHighlightOptions
)
from pygls.types.language_features.document_link import (
    DocumentLinkClientCapabilities,
    DocumentLinkOptions
)
from pygls.types.language_features.document_symbol import (
    DocumentSymbolClientCapabilities,
    DocumentSymbolOptions
)
from pygls.types.language_features.folding_range import (
    FoldingRangeClientCapabilities,
    FoldingRangeOptions,
    FoldingRangeRegistrationOptions
)
from pygls.types.language_features.formatting import (
    DocumentFormattingClientCapabilities,
    DocumentFormattingOptions
)
from pygls.types.language_features.hover import (
    HoverClientCapabilities,
    HoverOptions
)
from pygls.types.language_features.implementation import (
    ImplementationClientCapabilities,
    ImplementationOptions,
    ImplementationRegistrationOptions
)
from pygls.types.language_features.on_type_formatting import (
    DocumentOnTypeFormattingClientCapabilities,
    DocumentOnTypeFormattingOptions
)
from pygls.types.language_features.range_formatting import (
    DocumentRangeFormattingClientCapabilities,
    DocumentRangeFormattingOptions
)
from pygls.types.language_features.references import (
    ReferenceClientCapabilities,
    ReferenceOptions
)
from pygls.types.language_features.rename import (
    RenameClientCapabilities,
    RenameOptions
)
from pygls.types.language_features.selection_range import (
    SelectionRangeClientCapabilities,
    SelectionRangeOptions,
    SelectionRangeRegistrationOptions
)
from pygls.types.language_features.signature_help import (
    SignatureHelpClientCapabilities
)
from pygls.types.language_features.type_definition import (
    TypeDefinitionClientCapabilities,
    TypeDefinitionOptions,
    TypeDefinitionRegistrationOptions
)
from pygls.types.text_synchronization import TextDocumentSyncKind
from pygls.types.workspace import (
    DidChangeConfigurationClientCapabilities,
    DidChangeWatchedFilesClientCapabilities,
    ExecuteCommandClientCapabilities,
    ExecuteCommandOptions,
    SaveOptions,
    TextDocumentSyncClientCapabilities,
    WorkspaceFolder,
    WorkspaceFoldersServerCapabilities,
    WorkspaceSymbolClientCapabilities
)


class ClientInfo:
    def __init__(self, name: str = 'unknown', version: Optional[str] = None):
        self.name = name
        self.version = version


class ServerInfo:
    def __init__(self, name: str = 'unknown', version: Optional[str] = None):
        self.name = name
        self.version = version


class Trace(str, enum.Enum):
    Off = 'off'
    Messages = 'messages'
    Verbose = 'verbose'


class InitializeParams(WorkDoneProgressParams):
    def __init__(self,
                 process_id: Union[int, None],
                 root_uri: Union[str, None],
                 capabilities: 'ClientCapabilities',
                 client_info: Optional[ClientInfo] = None,
                 root_path: Optional[str] = None,
                 initialization_options: Optional[Any] = None,
                 trace: Optional[Trace] = Trace.Off,
                 workspace_folders: Optional[List[WorkspaceFolder]] = None,
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


class TextDocumentClientCapabilities:
    def __init__(self,
                 synchronization: Optional[TextDocumentSyncClientCapabilities] = None,
                 completion: Optional[CompletionClientCapabilities] = None,
                 hover: Optional[HoverClientCapabilities] = None,
                 signature_help: Optional[SignatureHelpClientCapabilities] = None,
                 declaration: Optional[DeclarationClientCapabilities] = None,
                 definition: Optional[DefinitionClientCapabilities] = None,
                 type_definition: Optional[TypeDefinitionClientCapabilities] = None,
                 implementation: Optional[ImplementationClientCapabilities] = None,
                 references: Optional[ReferenceClientCapabilities] = None,
                 document_highlight: Optional[DocumentHighlightClientCapabilities] = None,
                 document_symbol: Optional[DocumentSymbolClientCapabilities] = None,
                 code_action: Optional[CodeActionClientCapabilities] = None,
                 code_lens: Optional[CodeLensClientCapabilities] = None,
                 document_link: Optional[DocumentLinkClientCapabilities] = None,
                 color_provider: Optional[DocumentColorClientCapabilities] = None,
                 formatting: Optional[DocumentFormattingClientCapabilities] = None,
                 range_formatting: Optional[DocumentRangeFormattingClientCapabilities] = None,
                 on_type_formatting: Optional[DocumentOnTypeFormattingClientCapabilities] = None,
                 rename: Optional[RenameClientCapabilities] = None,
                 publish_diagnostics: Optional[PublishDiagnosticsClientCapabilities] = None,
                 folding_range: Optional[FoldingRangeClientCapabilities] = None,
                 selection_range: Optional[SelectionRangeClientCapabilities] = None):
        self.synchronization = synchronization
        self.completion = completion
        self.hover = hover
        self.signatureHelp = signature_help
        self.declaration = declaration
        self.definition = definition
        self.typeDefinition = type_definition
        self.implementation = implementation
        self.references = references
        self.documentHighlight = document_highlight
        self.documentSymbol = document_symbol
        self.codeAction = code_action
        self.codeLens = code_lens
        self.documentLink = document_link
        self.colorProvider = color_provider
        self.formatting = formatting
        self.rangeFormatting = range_formatting
        self.onTypeFormatting = on_type_formatting
        self.rename = rename
        self.publishDiagnostics = publish_diagnostics
        self.foldingRange = folding_range
        self.selectionRange = selection_range


class ClientCapabilities:
    def __init__(self,
                 workspace: Optional['WorkspaceClientCapabilities'] = None,
                 text_document: Optional[TextDocumentClientCapabilities] = None,
                 window: Optional['WindowClientCapabilities'] = None,
                 experimental: Optional[Any] = None):
        self.workspace = workspace
        self.textDocument = text_document
        self.window = window
        self.experimental = experimental


class WorkspaceClientCapabilities:
    def __init__(self,
                 apply_edit: Optional[bool] = False,
                 workspace_edit: Optional[WorkspaceEditClientCapabilities] = None,
                 did_change_configuration: Optional[DidChangeConfigurationClientCapabilities] = None,
                 did_change_watched_files: Optional[DidChangeWatchedFilesClientCapabilities] = None,
                 symbol: Optional[WorkspaceSymbolClientCapabilities] = None,
                 execute_command: Optional[ExecuteCommandClientCapabilities] = None,
                 workspace_folders: Optional[bool] = False,
                 configuration: Optional[bool] = False):
        self.applyEdit = apply_edit
        self.workspaceEdit = workspace_edit
        self.didChangeConfiguration = did_change_configuration
        self.didChangeWatched = did_change_watched_files
        self.symbol = symbol
        self.executeCommand = execute_command
        self.workspace_folders = workspace_folders
        self.configuration = configuration


class WindowClientCapabilities:
    def __init__(self, work_done_progress: Optional[bool] = False):
        self.workDoneProgress = work_done_progress


class InitializeResult:
    def __init__(self,
                 capabilities: 'ServerCapabilities',
                 server_info: Optional[ServerInfo] = None):
        self.capabilities = capabilities
        self.serverInfo = server_info


class ServerCapabilities:
    def __init__(self,
                 text_document_sync: Optional[Union['TextDocumentSyncOptionsServerCapabilities', NumType]] = None,
                 completion_provider: Optional[CompletionOptions] = None,
                 hover_provider: Optional[Union[bool, HoverOptions]] = None,
                 signature_help_provider: Optional['SignatureHelpOptions'] = None,
                 declaration_provider: Optional[Union[bool, DeclarationOptions, DeclarationRegistrationOptions]] = None,
                 definition_provider: Optional[Union[bool, DefinitionOptions]] = None,
                 type_definition_provider: Optional[Union[bool, TypeDefinitionOptions, TypeDefinitionRegistrationOptions]] = None,
                 implementation_provider: Optional[Union[bool, ImplementationOptions, ImplementationRegistrationOptions]] = None,
                 references_provider: Optional[Union[bool, ReferenceOptions]] = None,
                 document_highlight_provider: Optional[Union[bool, DocumentHighlightOptions]] = None,
                 document_symbol_provider: Optional[Union[bool, DocumentSymbolOptions]] = None,
                 code_action_provider: Optional[Union[bool, CodeActionOptions]] = None,
                 code_lens_provider: Optional[CodeLensOptions] = None,
                 document_link_provider: Optional[DocumentLinkOptions] = None,
                 color_provider: Optional[Union[bool, DocumentColorOptions, DocumentColorRegistrationOptions]] = None,
                 document_formatting_provider: Optional[Union[bool, DocumentFormattingOptions]] = None,
                 document_range_formatting_provider: Optional[Union[bool, DocumentRangeFormattingOptions]] = None,
                 document_on_type_formatting_provider: Optional[DocumentOnTypeFormattingOptions] = None,
                 rename_provider: Optional[Union[bool, RenameOptions]] = None,
                 folding_range_provider: Optional[Union[bool, FoldingRangeOptions, FoldingRangeRegistrationOptions]] = None,
                 execute_command_provider: Optional[ExecuteCommandOptions] = None,
                 selection_range_provider: Optional[Union[bool, SelectionRangeOptions, SelectionRangeRegistrationOptions]] = None,
                 workspace_symbol_provider: Optional[bool] = None,
                 workspace: Optional['WorkspaceServerCapabilities'] = None,
                 experimental: Optional[Any] = None):
        self.textDocumentSync = text_document_sync
        self.completionProvider = completion_provider
        self.hoverProvider = hover_provider
        self.signatureHelpProvider = signature_help_provider
        self.declarationProvider = declaration_provider
        self.definitionProvider = definition_provider
        self.typeDefinitionProvider = type_definition_provider
        self.implementationProvider = implementation_provider
        self.referencesProvider = references_provider
        self.documentHighlightProvider = document_highlight_provider
        self.documentSymbolProvider = document_symbol_provider
        self.codeActionProvider = code_action_provider
        self.codeLensProvider = code_lens_provider
        self.documentLinkProvider = document_link_provider
        self.colorProvider = color_provider
        self.documentFormattingProvider = document_formatting_provider
        self.documentRangeFormattingProvider = document_range_formatting_provider
        self.documentOnTypeFormattingProvider = document_on_type_formatting_provider
        self.renameProvider = rename_provider
        self.foldingRangeProvider = folding_range_provider
        self.executeCommandProvider = execute_command_provider
        self.selectionRangeProvider = selection_range_provider
        self.workspaceSymbolProvider = workspace_symbol_provider
        self.workspace = workspace
        self.experimental = experimental


class TextDocumentSyncOptionsServerCapabilities:
    def __init__(self,
                 open_close: Optional[bool] = False,
                 change: Optional[TextDocumentSyncKind] = TextDocumentSyncKind.NONE,
                 will_save: Optional[bool] = False,
                 will_save_wait_until: Optional[bool] = False,
                 save: Optional[Union[bool, SaveOptions]] = None):
        self.openClose = open_close
        self.change = change
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.save = save


class WorkspaceServerCapabilities:
    def __init__(self,
                 workspace_folders: Optional[List[WorkspaceFoldersServerCapabilities]] = None):
        self.workspaceFolders = workspace_folders


class InitializedParams:
    pass
