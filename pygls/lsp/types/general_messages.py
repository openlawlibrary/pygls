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

Class attributes are named with camel case notation because client is expecting
that.
"""
from functools import reduce
from typing import Any, List, Optional, Union

from pygls.lsp.types.basic_structures import (Model, NumType, RegularExpressionsClientCapabilities,
                                              Trace, WorkDoneProgressParams,
                                              WorkspaceEditClientCapabilities)
from pygls.lsp.types.diagnostics import PublishDiagnosticsClientCapabilities
from pygls.lsp.types.file_operations import FileOperationRegistrationOptions
from pygls.lsp.types.language_features import (CallHierarchyClientCapabilities,
                                               CallHierarchyOptions,
                                               CallHierarchyRegistrationOptions,
                                               CodeActionClientCapabilities, CodeActionOptions,
                                               CodeLensClientCapabilities, CodeLensOptions,
                                               CodeLensWorkspaceClientCapabilities,
                                               CompletionClientCapabilities, CompletionOptions,
                                               DeclarationClientCapabilities, DeclarationOptions,
                                               DeclarationRegistrationOptions,
                                               DefinitionClientCapabilities, DefinitionOptions,
                                               DocumentColorClientCapabilities,
                                               DocumentColorOptions,
                                               DocumentColorRegistrationOptions,
                                               DocumentFormattingClientCapabilities,
                                               DocumentFormattingOptions,
                                               DocumentHighlightClientCapabilities,
                                               DocumentHighlightOptions,
                                               DocumentLinkClientCapabilities, DocumentLinkOptions,
                                               DocumentOnTypeFormattingClientCapabilities,
                                               DocumentOnTypeFormattingOptions,
                                               DocumentRangeFormattingClientCapabilities,
                                               DocumentRangeFormattingOptions,
                                               DocumentSymbolClientCapabilities,
                                               DocumentSymbolOptions,
                                               FoldingRangeClientCapabilities, FoldingRangeOptions,
                                               FoldingRangeRegistrationOptions,
                                               HoverClientCapabilities, HoverOptions,
                                               ImplementationClientCapabilities,
                                               ImplementationOptions,
                                               ImplementationRegistrationOptions,
                                               LinkedEditingRangeClientCapabilities,
                                               LinkedEditingRangeOptions,
                                               LinkedEditingRangeRegistrationOptions,
                                               MonikerClientCapabilities, MonikerOptions,
                                               MonikerRegistrationOptions,
                                               ReferenceClientCapabilities, ReferenceOptions,
                                               RenameClientCapabilities, RenameOptions,
                                               SelectionRangeClientCapabilities,
                                               SelectionRangeOptions,
                                               SelectionRangeRegistrationOptions,
                                               SemanticTokensClientCapabilities,
                                               SemanticTokensOptions,
                                               SemanticTokensRegistrationOptions,
                                               SemanticTokensWorkspaceClientCapabilities,
                                               SignatureHelpClientCapabilities,
                                               SignatureHelpOptions,
                                               TypeDefinitionClientCapabilities,
                                               TypeDefinitionOptions,
                                               TypeDefinitionRegistrationOptions)
from pygls.lsp.types.text_synchronization import TextDocumentSyncKind
from pygls.lsp.types.window import (ShowDocumentClientCapabilities,
                                    ShowMessageRequestClientCapabilities)
from pygls.lsp.types.workspace import (DidChangeConfigurationClientCapabilities,
                                       DidChangeWatchedFilesClientCapabilities,
                                       ExecuteCommandClientCapabilities, ExecuteCommandOptions,
                                       SaveOptions, TextDocumentSyncClientCapabilities,
                                       WorkspaceFolder, WorkspaceFoldersServerCapabilities,
                                       WorkspaceSymbolClientCapabilities)


class ClientInfo(Model):
    name: str = 'unknown'
    version: Optional[str] = None


class ServerInfo(Model):
    name: str = 'unknown'
    version: Optional[str] = None


class TextDocumentClientCapabilities(Model):
    synchronization: Optional[TextDocumentSyncClientCapabilities] = None
    completion: Optional[CompletionClientCapabilities] = None
    hover: Optional[HoverClientCapabilities] = None
    signature_help: Optional[SignatureHelpClientCapabilities] = None
    declaration: Optional[DeclarationClientCapabilities] = None
    definition: Optional[DefinitionClientCapabilities] = None
    type_definition: Optional[TypeDefinitionClientCapabilities] = None
    implementation: Optional[ImplementationClientCapabilities] = None
    references: Optional[ReferenceClientCapabilities] = None
    document_highlight: Optional[DocumentHighlightClientCapabilities] = None
    document_symbol: Optional[DocumentSymbolClientCapabilities] = None
    code_action: Optional[CodeActionClientCapabilities] = None
    code_lens: Optional[CodeLensClientCapabilities] = None
    document_link: Optional[DocumentLinkClientCapabilities] = None
    color_provider: Optional[DocumentColorClientCapabilities] = None
    formatting: Optional[DocumentFormattingClientCapabilities] = None
    range_formatting: Optional[DocumentRangeFormattingClientCapabilities] = None
    on_type_formatting: Optional[DocumentOnTypeFormattingClientCapabilities] = None
    rename: Optional[RenameClientCapabilities] = None
    publish_diagnostics: Optional[PublishDiagnosticsClientCapabilities] = None
    folding_range: Optional[FoldingRangeClientCapabilities] = None
    selection_range: Optional[SelectionRangeClientCapabilities] = None
    linked_editing_range: Optional[LinkedEditingRangeClientCapabilities] = None
    call_hierarchy: Optional[CallHierarchyClientCapabilities] = None
    semantic_tokens: Optional[SemanticTokensClientCapabilities] = None
    moniker: Optional[MonikerClientCapabilities] = None


class FileOperationsClientCapabilities(Model):
    dynamic_registration: Optional[bool] = False
    did_create: Optional[bool] = False
    will_create: Optional[bool] = False
    did_rename: Optional[bool] = False
    will_rename: Optional[bool] = False
    did_delete: Optional[bool] = False
    will_delete: Optional[bool] = False


class WorkspaceClientCapabilities(Model):
    apply_edit: Optional[bool] = False
    workspace_edit: Optional[WorkspaceEditClientCapabilities] = None
    did_change_configuration: Optional[DidChangeConfigurationClientCapabilities] = None
    did_change_watched_files: Optional[DidChangeWatchedFilesClientCapabilities] = None
    symbol: Optional[WorkspaceSymbolClientCapabilities] = None
    execute_command: Optional[ExecuteCommandClientCapabilities] = None
    workspace_folders: Optional[bool] = False
    configuration: Optional[bool] = False
    semantic_tokens: Optional[SemanticTokensWorkspaceClientCapabilities] = None
    code_lens: Optional[CodeLensWorkspaceClientCapabilities] = None
    file_operations: Optional[FileOperationsClientCapabilities] = None


class WindowClientCapabilities(Model):
    work_done_progress: Optional[bool] = False
    show_message: Optional[ShowMessageRequestClientCapabilities] = None
    show_document: Optional[ShowDocumentClientCapabilities] = None


class MarkdownClientCapabilities(Model):
    parser: str
    version: Optional[str] = None


class GeneralClientCapabilities(Model):
    regular_expressions: Optional[RegularExpressionsClientCapabilities] = None
    markdown: Optional[MarkdownClientCapabilities] = None


class TextDocumentSyncOptionsServerCapabilities(Model):
    open_close: Optional[bool] = False
    change: Optional[TextDocumentSyncKind] = TextDocumentSyncKind.NONE
    will_save: Optional[bool] = False
    will_save_wait_until: Optional[bool] = False
    save: Optional[Union[bool, SaveOptions]] = None


class WorkspaceFileOperationsServerCapabilities(Model):
    did_create: Optional[FileOperationRegistrationOptions] = None
    will_create: Optional[FileOperationRegistrationOptions] = None
    did_rename: Optional[FileOperationRegistrationOptions] = None
    will_rename: Optional[FileOperationRegistrationOptions] = None
    did_delete: Optional[FileOperationRegistrationOptions] = None
    will_delete: Optional[FileOperationRegistrationOptions] = None


class WorkspaceServerCapabilities(Model):
    workspace_folders: Optional[WorkspaceFoldersServerCapabilities] = None
    file_operations: Optional[WorkspaceFileOperationsServerCapabilities] = None


class ClientCapabilities(Model):
    workspace: Optional[WorkspaceClientCapabilities] = None
    text_document: Optional[TextDocumentClientCapabilities] = None
    window: Optional[WindowClientCapabilities] = None
    general: Optional[GeneralClientCapabilities] = None
    experimental: Optional[Any] = None

    def get_capability(self, field: str, default: Any = None) -> Any:
        """Check if ClientCapabilities has some nested value without raising
        AttributeError.

        e.g. get_capability('text_document.synchronization.will_save')
        """
        try:
            value = reduce(getattr, field.split("."), self)
        except AttributeError:
            return default

        # If we reach the desired leaf value but it's None, return the default.
        value = default if value is None else value
        return value


class InitializeParams(WorkDoneProgressParams):
    process_id: Optional[int] = None
    root_uri: Optional[str] = None
    capabilities: ClientCapabilities
    client_info: Optional[ClientInfo] = None
    locale: Optional[str] = None
    root_path: Optional[str] = None
    initialization_options: Optional[Any] = None
    trace: Optional[Trace] = Trace.Off
    workspace_folders: Optional[List[WorkspaceFolder]] = None


class ServerCapabilities(Model):
    text_document_sync: Optional[Union[TextDocumentSyncOptionsServerCapabilities, NumType]] = None
    completion_provider: Optional[CompletionOptions] = None
    hover_provider: Optional[Union[bool, HoverOptions]] = None
    signature_help_provider: Optional[SignatureHelpOptions] = None
    declaration_provider: Optional[Union[bool, DeclarationOptions,
                                         DeclarationRegistrationOptions]] = None
    definition_provider: Optional[Union[bool, DefinitionOptions]] = None
    type_definition_provider: Optional[Union[bool, TypeDefinitionOptions,
                                             TypeDefinitionRegistrationOptions]] = None
    implementation_provider: Optional[Union[bool, ImplementationOptions,
                                            ImplementationRegistrationOptions]] = None
    references_provider: Optional[Union[bool, ReferenceOptions]] = None
    document_highlight_provider: Optional[Union[bool, DocumentHighlightOptions]] = None
    document_symbol_provider: Optional[Union[bool, DocumentSymbolOptions]] = None
    code_action_provider: Optional[Union[bool, CodeActionOptions]] = None
    code_lens_provider: Optional[CodeLensOptions] = None
    document_link_provider: Optional[DocumentLinkOptions] = None
    color_provider: Optional[Union[bool, DocumentColorOptions,
                                   DocumentColorRegistrationOptions]] = None
    document_formatting_provider: Optional[Union[bool, DocumentFormattingOptions]] = None
    document_range_formatting_provider: Optional[Union[bool,
                                                       DocumentRangeFormattingOptions]] = None
    document_on_type_formatting_provider: Optional[DocumentOnTypeFormattingOptions] = None
    rename_provider: Optional[Union[bool, RenameOptions]] = None
    folding_range_provider: Optional[Union[bool, FoldingRangeOptions,
                                           FoldingRangeRegistrationOptions]] = None
    execute_command_provider: Optional[ExecuteCommandOptions] = None
    selection_range_provider: Optional[Union[bool, SelectionRangeOptions,
                                             SelectionRangeRegistrationOptions]] = None
    linked_editing_range_provider: Optional[Union[bool, LinkedEditingRangeOptions,
                                                  LinkedEditingRangeRegistrationOptions]] = None
    call_hierarchy_provider: Optional[Union[bool, CallHierarchyOptions,
                                            CallHierarchyRegistrationOptions]] = None
    semantic_tokens_provider: Optional[Union[SemanticTokensOptions,
                                             SemanticTokensRegistrationOptions]] = None
    moniker_provider: Optional[Union[bool, MonikerOptions,
                                     MonikerRegistrationOptions]] = None
    workspace_symbol_provider: Optional[bool] = None
    workspace: Optional[WorkspaceServerCapabilities] = None
    experimental: Optional[Any] = None


class InitializeResult(Model):
    capabilities: ServerCapabilities
    server_info: Optional[ServerInfo] = None


class InitializedParams(Model):
    pass
