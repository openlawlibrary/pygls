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
from pygls.lsp.methods import (CODE_ACTION, CODE_LENS, COMPLETION, DECLARATION, DEFINITION,
                               DOCUMENT_COLOR, DOCUMENT_HIGHLIGHT, DOCUMENT_LINK, DOCUMENT_SYMBOL,
                               FOLDING_RANGE, FORMATTING, HOVER, IMPLEMENTATION,
                               ON_TYPE_FORMATTING, RANGE_FORMATTING, REFERENCES, RENAME,
                               SELECTION_RANGE, SIGNATURE_HELP, TEXT_DOCUMENT_DID_CLOSE,
                               TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_SAVE,
                               TEXT_DOCUMENT_WILL_SAVE, TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL,
                               TYPE_DEFINITION, WORKSPACE_SYMBOL)
from pygls.lsp.types import (CodeLensOptions, CompletionOptions, DocumentLinkOptions,
                             ExecuteCommandOptions, ImplementationOptions, SaveOptions,
                             ServerCapabilities, SignatureHelpOptions,
                             TextDocumentSyncOptionsServerCapabilities, TypeDefinitionOptions,
                             WorkspaceFoldersServerCapabilities, WorkspaceServerCapabilities)


class ServerCapabilitiesBuilder:
    """Create `ServerCapabilities` instance depending on builtin and user registered
    features.
    """
    def __init__(
        self,
        client_capabilities,
        features,
        feature_options,
        commands,
        sync_kind
    ):
        self.client_capabilities = client_capabilities
        self.features = features
        self.feature_options = feature_options
        self.commands = commands
        self.sync_kind = sync_kind

        self.server_cap = ServerCapabilities()

    def _provider_options(self, feature, default=True):
        if feature in self.features:
            if feature in self.feature_options:
                return self.feature_options[feature]
            else:
                return default
        return None

    def _with_text_doc_sync(self):
        open_close = (
            TEXT_DOCUMENT_DID_OPEN in self.features
            or TEXT_DOCUMENT_DID_CLOSE in self.features
        )
        will_save = (
            self.client_capabilities.get_capability(
                'text_document.synchronization.will_save')
            and TEXT_DOCUMENT_WILL_SAVE in self.features
        )
        will_save_wait_until = (
            self.client_capabilities.get_capability(
                'text_document.synchronization.will_save_wait_until')
            and TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL in self.features
        )
        if TEXT_DOCUMENT_DID_SAVE in self.features:
            if TEXT_DOCUMENT_DID_SAVE in self.feature_options:
                include_text = self.feature_options[TEXT_DOCUMENT_DID_SAVE].include_text
                save = SaveOptions(include_text=include_text)
            else:
                save = True
        else:
            save = False

        self.server_cap.text_document_sync = TextDocumentSyncOptionsServerCapabilities(
            open_close=open_close,
            change=self.sync_kind,
            will_save=will_save,
            will_save_wait_until=will_save_wait_until,
            save=save,
        )

        return self

    def _with_completion(self):
        self.server_cap.completion_provider = \
            self._provider_options(COMPLETION, default=CompletionOptions())
        return self

    def _with_hover(self):
        self.server_cap.hover_provider = self._provider_options(HOVER)
        return self

    def _with_signature_help(self):
        self.server_cap.signature_help_provider = \
            self._provider_options(SIGNATURE_HELP,
                                   default=SignatureHelpOptions())
        return self

    def _with_declaration(self):
        self.server_cap.declaration_provider = \
            self._provider_options(DECLARATION)
        return self

    def _with_definition(self):
        self.server_cap.definition_provider = self._provider_options(DEFINITION)
        return self

    def _with_type_definition(self):
        self.server_cap.type_definition_provider = \
            self._provider_options(TYPE_DEFINITION,
                                   default=TypeDefinitionOptions())
        return self

    def _with_implementation(self):
        self.server_cap.implementation_provider = \
            self._provider_options(IMPLEMENTATION,
                                   default=ImplementationOptions())
        return self

    def _with_references(self):
        self.server_cap.references_provider = self._provider_options(REFERENCES)
        return self

    def _with_document_highlight(self):
        self.server_cap.document_highlight_provider = \
            self._provider_options(DOCUMENT_HIGHLIGHT)
        return self

    def _with_document_symbol(self):
        self.server_cap.document_symbol_provider = \
            self._provider_options(DOCUMENT_SYMBOL)
        return self

    def _with_code_action(self):
        self.server_cap.code_action_provider = \
            self._provider_options(CODE_ACTION)
        return self

    def _with_code_lens(self):
        self.server_cap.code_lens_provider = \
            self._provider_options(CODE_LENS,
                                   default=CodeLensOptions())
        return self

    def _with_document_link(self):
        self.server_cap.document_link_provider = \
            self._provider_options(DOCUMENT_LINK,
                                   default=DocumentLinkOptions())
        return self

    def _with_color(self):
        self.server_cap.color_provider = \
            self._provider_options(DOCUMENT_COLOR)
        return self

    def _with_document_formatting(self):
        self.server_cap.document_formatting_provider = \
            self._provider_options(FORMATTING)
        return self

    def _with_document_range_formatting(self):
        self.server_cap.document_range_formatting_provider = \
            self._provider_options(RANGE_FORMATTING)
        return self

    def _with_document_on_type_formatting(self):
        self.server_cap.document_on_type_formatting_provider = \
            self._provider_options(ON_TYPE_FORMATTING)
        return self

    def _with_rename(self):
        self.server_cap.rename_provider = self._provider_options(RENAME)
        return self

    def _with_folding_range(self):
        self.server_cap.folding_range_provider = \
            self._provider_options(FOLDING_RANGE)
        return self

    def _with_execute_command(self):
        self.server_cap.execute_command_provider = \
            ExecuteCommandOptions(commands=self.commands)
        return self

    def _with_selection_range(self):
        self.server_cap.selection_range_provider = \
            self._provider_options(SELECTION_RANGE)
        return self

    def _with_workspace_symbol(self):
        self.server_cap.workspace_symbol_provider = \
            self._provider_options(WORKSPACE_SYMBOL)
        return self

    def _with_workspace_capabilities(self):
        self.server_cap.workspace = WorkspaceServerCapabilities(
            workspace_folders=WorkspaceFoldersServerCapabilities(
                supported=True,
                change_notifications=True,
            )
        )
        return self

    def _build(self):
        return self.server_cap

    def build(self):
        return (
            self
            ._with_text_doc_sync()
            ._with_completion()
            ._with_hover()
            ._with_signature_help()
            ._with_declaration()
            ._with_definition()
            ._with_type_definition()
            ._with_implementation()
            ._with_references()
            ._with_document_highlight()
            ._with_document_symbol()
            ._with_code_action()
            ._with_code_lens()
            ._with_document_link()
            ._with_color()
            ._with_document_formatting()
            ._with_document_range_formatting()
            ._with_document_on_type_formatting()
            ._with_rename()
            ._with_folding_range()
            ._with_execute_command()
            ._with_selection_range()
            ._with_workspace_symbol()
            ._with_workspace_capabilities()
            ._build()
        )
