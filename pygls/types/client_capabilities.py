from typing import Any, List, Optional

from pygls.types.common import (CompletionItemKind, CompletionItemTag, DiagnosticTag,
                                FailureHandlingKind, MarkupKind, NumType, ResourceOperationKind,
                                SymbolKind)


class DidChangeConfigurationClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DidChangeWatchedFilesClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class WorkspaceCapabilitiesSymbolKind:
    def __init__(self, value_set: Optional[List[SymbolKind]] = None):
        self.valueSet = value_set


class WorkspaceSymbolClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 symbol_kind: Optional[WorkspaceCapabilitiesSymbolKind] = None):
        self.dynamicRegistration = dynamic_registration
        self.symbolKind = symbol_kind


class ExecuteCommandClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class WorkspaceEditClientCapabilities:
    def __init__(self,
                 document_changes: Optional[bool] = False,
                 resource_operations: Optional[List[ResourceOperationKind]] = None,
                 failure_handling: Optional[FailureHandlingKind] = None):
        self.documentChanges = document_changes
        self.resourceOperations = resource_operations
        self.failureHandling = failure_handling


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


class TextDocumentSyncClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 will_save: Optional[bool] = False,
                 will_save_wait_until: Optional[bool] = False,
                 did_save: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.willSave = will_save
        self.willSaveWaitUntil = will_save_wait_until
        self.didSave = did_save


class CompletionTagSupportClientCapabilities:
    def __init__(self, value_set: Optional[List[CompletionItemTag]] = None):
        self.valueSet = value_set


class CompletionItemClientCapabilities:
    def __init__(self,
                 snippet_support: Optional[bool] = False,
                 commit_character_support: Optional[bool] = False,
                 documentation_format: Optional[List[MarkupKind]] = None,
                 deprecated_support: Optional[bool] = False,
                 preselected_support: Optional[bool] = False,
                 tag_support: Optional[CompletionTagSupportClientCapabilities] = False):
        self.snippetSupport = snippet_support
        self.commitCharacterSupport = commit_character_support
        self.documentationFormat = documentation_format
        self.deprecatedSupport = deprecated_support
        self.preselectedSupport = preselected_support
        self.tagSupport = tag_support


class CompletionItemKindClientCapabilities:
    def __init__(self, value_set: Optional[List[CompletionItemKind]] = None):
        self.valueSet = value_set


class CompletionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 completion_item: Optional[CompletionItemClientCapabilities] = None,
                 completion_item_kind: Optional[CompletionItemKindClientCapabilities] = None,
                 context_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.completionItem = completion_item
        self.completionItemKind = completion_item_kind
        self.contextSupport = context_support


class HoverClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 content_format: Optional[List[MarkupKind]] = None):
        self.dynamicRegistration = dynamic_registration
        self.contentFormat = content_format


class SignatureHelpInformationParameterInformationClientCapabilities:
    def __init__(self, label_offset_support: Optional[bool] = False):
        self.labelOffsetSupport = label_offset_support


class SignatureHelpInformationClientCapabilities:
    def __init__(self,
                 documentation_format: Optional[List[MarkupKind]] = None,
                 parameter_information: Optional[SignatureHelpInformationParameterInformationClientCapabilities] = None):
        self.documentationFormat = documentation_format
        self.parameterInformation = parameter_information


class SignatureHelpClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 signature_information: Optional[SignatureHelpInformationClientCapabilities] = None,
                 contextSupport: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.signatureInformation = signature_information


class DeclarationClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 link_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.linkSupport = link_support


class DefinitionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 link_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.linkSupport = link_support


class TypeDefinitionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 link_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.linkSupport = link_support


class ImplementationClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 link_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.linkSupport = link_support


class ReferenceClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentHighlightClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentSymbolClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 symbol_kind: Optional[WorkspaceCapabilitiesSymbolKind] = None,
                 hierarchical_document_symbol_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration,
        self.symbolKind = symbol_kind
        self.hierarchicalDocumentSymbolSupport = hierarchical_document_symbol_support


class CodeActionLiteralSupportActionKindClientCapabilities:
    def __init__(self, value_set: Optional[List[SymbolKind]] = None):
        self.valueSet = value_set


class CodeActionLiteralSupportClientCapabilities:
    def __init__(self,
                 code_action_kind: Optional[CodeActionLiteralSupportActionKindClientCapabilities] = None):
        self.codeActionKind = code_action_kind


class CodeActionClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 code_action_literal_support: Optional[CodeActionLiteralSupportClientCapabilities] = None,
                 is_preferred_support: Optional[bool] = False,):
        self.dynamicRegistration = dynamic_registration
        self.codeActionLiteralSupport = code_action_literal_support
        self.isPreferredSupport = is_preferred_support


class CodeLensClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentLinkClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 tooltip_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.tooltipSupport = tooltip_support


class DocumentColorClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentFormattingClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentRangeFormattingClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class DocumentOnTypeFormattingClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


class RenameClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 prepare_support: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration
        self.prepareSupport = prepare_support


class PublishDiagnosticsTagSupportClientCapabilities:
    def __init__(self, value_set: Optional[List[DiagnosticTag]] = None):
        self.valueSet = value_set


class PublishDiagnosticsClientCapabilities:
    def __init__(self,
                 related_information: Optional[bool] = False,
                 tag_support: Optional[PublishDiagnosticsTagSupportClientCapabilities] = None,
                 version_support: Optional[bool] = False):
        self.relatedInformation = related_information
        self.tagSupport = tag_support
        self.versionSupport = version_support


class FoldingRangeClientCapabilities:
    def __init__(self,
                 dynamic_registration: Optional[bool] = False,
                 range_limit: Optional[NumType] = None,
                 line_folding_only: Optional[bool] = False,):
        self.dynamicRegistration = dynamic_registration
        self.rangeLimit = range_limit
        self.lineFoldingOnly = line_folding_only


class SelectionRangeClientCapabilities:
    def __init__(self, dynamic_registration: Optional[bool] = False):
        self.dynamicRegistration = dynamic_registration


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


class WindowClientCapabilities:
    def __init__(self, work_done_progress: Optional[bool] = False):
        self.workDoneProgress = work_done_progress


class ClientCapabilities:
    def __init__(self,
                 workspace: Optional[WorkspaceClientCapabilities] = None,
                 text_document: Optional[TextDocumentClientCapabilities] = None,
                 window: Optional[WindowClientCapabilities] = None,
                 experimental: Optional[Any] = None):
        self.workspace = workspace
        self.textDocument = text_document
        self.window = window
        self.experimental = experimental
