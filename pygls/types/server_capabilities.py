from typing import Any, List, Optional, Union

from pygls.types.common import (CodeActionKind, DocumentSelectorType, NumType, ProgressToken,
                                TextDocumentSyncKind, WorkDoneProgressOptions)


class StaticRegistrationOptions:
    def __init__(self, id: Optional[str] = None):
        self.id = id


class TextDocumentRegistrationOptions:
    def __init__(self, document_selector: Optional[DocumentSelectorType] = None):
        self.documentSelector = document_selector


class SaveOptions:
    def __init__(self, include_text: bool = False):
        self.includeText = include_text


class TextDocumentSyncOptions:
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


class CompletionOptions(WorkDoneProgressOptions):
    def __init__(self,
                 trigger_characters: Optional[List[str]] = None,
                 all_commit_characters: Optional[List[str]] = None,
                 resolve_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.triggerCharacters = trigger_characters
        self.allCommitCharacters = all_commit_characters
        self.resolveProvider = resolve_provider


class HoverOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class SignatureHelpOptions(WorkDoneProgressOptions):
    def __init__(self,
                 trigger_characters: Optional[List[str]] = None,
                 retrigger_characters: Optional[List[str]] = None,
                 work_done_progress: Optional[ProgressToken] = None
                 ):
        super().__init__(work_done_progress)
        self.triggerCharacters = trigger_characters
        self.retriggerCharacters = retrigger_characters


class DeclarationOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DeclarationRegistrationOptions(DeclarationOptions,
                                     TextDocumentRegistrationOptions,
                                     StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        DeclarationOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class DefinitionOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class TypeDefinitionOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class TypeDefinitionRegistrationOptions(TypeDefinitionOptions,
                                        TextDocumentRegistrationOptions,
                                        StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        TypeDefinitionOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class ImplementationOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class ImplementationRegistrationOptions(ImplementationOptions,
                                        TextDocumentRegistrationOptions,
                                        StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        ImplementationOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class ReferenceOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentHighlightOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentSymbolOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class CodeActionOptions(WorkDoneProgressOptions):
    def __init__(self,
                 code_action_kinds: Optional[List[CodeActionKind]] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.codeActionKinds = code_action_kinds


class CodeLensOptions(WorkDoneProgressOptions):
    def __init__(self,
                 resolve_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.resolveProvider = resolve_provider


class DocumentLinkOptions(WorkDoneProgressOptions):
    def __init__(self,
                 resolve_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.resolveProvider = resolve_provider


class DocumentColorOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentColorRegistrationOptions(DocumentColorOptions,
                                       TextDocumentRegistrationOptions,
                                       StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        DocumentColorOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class DocumentFormattingOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentRangeFormattingOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class DocumentOnTypeFormattingOptions(WorkDoneProgressOptions):
    def __init__(self,
                 first_trigger_character: str,
                 more_trigger_character: Optional[List[str]] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.firstTriggerCharacter = first_trigger_character
        self.moreTriggerCharacter = more_trigger_character


class RenameOptions(WorkDoneProgressOptions):
    def __init__(self,
                 prepare_provider: Optional[bool] = False,
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.prepareProvider = prepare_provider


class FoldingRangeOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class FoldingRangeRegistrationOptions(FoldingRangeOptions,
                                      TextDocumentRegistrationOptions,
                                      StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        FoldingRangeOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class ExecuteCommandOptions(WorkDoneProgressOptions):
    def __init__(self,
                 commands: List[str],
                 work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)
        self.commands = commands


class SelectionRangeOptions(WorkDoneProgressOptions):
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        super().__init__(work_done_progress)


class SelectionRangeRegistrationOptions(SelectionRangeOptions,
                                        TextDocumentRegistrationOptions,
                                        StaticRegistrationOptions):
    def __init__(self,
                 id: Optional[str] = None,
                 document_selector: Optional[DocumentSelectorType] = None,
                 work_done_progress: Optional[ProgressToken] = None):
        SelectionRangeOptions.__init__(self, work_done_progress)
        TextDocumentRegistrationOptions.__init__(self, document_selector)
        StaticRegistrationOptions.__init__(self, id)


class WorkspaceFoldersServerCapabilities:
    def __init__(self,
                 supported: Optional[bool] = False,
                 change_notifications: Optional[Union[str, bool]] = None):
        self.supported = supported
        self.changeNotifications = change_notifications


class WorkspaceServerCapabilities:
    def __init__(self,
                 workspace_folders: Optional[List[WorkspaceFoldersServerCapabilities]] = None):
        self.workspaceFolders = workspace_folders


class ServerCapabilities:
    def __init__(self,
                 text_document_sync: Optional[Union[TextDocumentSyncOptions, NumType]] = None,
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
                 workspace: Optional[WorkspaceServerCapabilities] = None,
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

    @classmethod
    def build(cls):
        # TODO: Build server capabilities from client capabilities, features, ...
        return cls()
