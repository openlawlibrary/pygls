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

# GENERATED FROM scripts/generate_code.py -- DO NOT EDIT
# flake8: noqa
from __future__ import annotations

from lsprotocol import types
from pygls.protocol import LanguageServerProtocol
from pygls.protocol import default_converter
from pygls.server import JsonRPCServer
import typing

if typing.TYPE_CHECKING:
    from cattrs import Converter
    from concurrent.futures import Future
    from typing import Any
    from typing import Callable
    from typing import Optional
    from typing import Sequence


class BaseLanguageServer(JsonRPCServer):

    protocol: LanguageServerProtocol

    def __init__(
        self,
        protocol_cls: type[LanguageServerProtocol] = LanguageServerProtocol,
        converter_factory: Callable[[], Converter] = default_converter,
        max_workers: int | None = None,
    ):
        super().__init__(protocol_cls, converter_factory, max_workers)

    def client_register_capability(
        self,
        params: types.RegistrationParams,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`client/registerCapability` request.

        The `client/registerCapability` request is sent from the server to the client to register a new capability
        handler on the client side.
        """
        return self.protocol.send_request("client/registerCapability", params, callback)

    async def client_register_capability_async(
        self,
        params: types.RegistrationParams,
    ) -> None:
        """Make a :lsp:`client/registerCapability` request.

        The `client/registerCapability` request is sent from the server to the client to register a new capability
        handler on the client side.
        """
        return await self.protocol.send_request_async("client/registerCapability", params)

    def client_unregister_capability(
        self,
        params: types.UnregistrationParams,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`client/unregisterCapability` request.

        The `client/unregisterCapability` request is sent from the server to the client to unregister a previously registered capability
        handler on the client side.
        """
        return self.protocol.send_request("client/unregisterCapability", params, callback)

    async def client_unregister_capability_async(
        self,
        params: types.UnregistrationParams,
    ) -> None:
        """Make a :lsp:`client/unregisterCapability` request.

        The `client/unregisterCapability` request is sent from the server to the client to unregister a previously registered capability
        handler on the client side.
        """
        return await self.protocol.send_request_async("client/unregisterCapability", params)

    def window_show_document(
        self,
        params: types.ShowDocumentParams,
        callback: Optional[Callable[[types.ShowDocumentResult], None]] = None,
    ) -> Future[types.ShowDocumentResult]:
        """Make a :lsp:`window/showDocument` request.

        A request to show a document. This request might open an
        external program depending on the value of the URI to open.
        For example a request to open `https://code.visualstudio.com/`
        will very likely open the URI in a WEB browser.

        @since 3.16.0
        """
        return self.protocol.send_request("window/showDocument", params, callback)

    async def window_show_document_async(
        self,
        params: types.ShowDocumentParams,
    ) -> types.ShowDocumentResult:
        """Make a :lsp:`window/showDocument` request.

        A request to show a document. This request might open an
        external program depending on the value of the URI to open.
        For example a request to open `https://code.visualstudio.com/`
        will very likely open the URI in a WEB browser.

        @since 3.16.0
        """
        return await self.protocol.send_request_async("window/showDocument", params)

    def window_show_message_request(
        self,
        params: types.ShowMessageRequestParams,
        callback: Optional[Callable[[Optional[types.MessageActionItem]], None]] = None,
    ) -> Future[Optional[types.MessageActionItem]]:
        """Make a :lsp:`window/showMessageRequest` request.

        The show message request is sent from the server to the client to show a message
        and a set of options actions to the user.
        """
        return self.protocol.send_request("window/showMessageRequest", params, callback)

    async def window_show_message_request_async(
        self,
        params: types.ShowMessageRequestParams,
    ) -> Optional[types.MessageActionItem]:
        """Make a :lsp:`window/showMessageRequest` request.

        The show message request is sent from the server to the client to show a message
        and a set of options actions to the user.
        """
        return await self.protocol.send_request_async("window/showMessageRequest", params)

    def window_work_done_progress_create(
        self,
        params: types.WorkDoneProgressCreateParams,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`window/workDoneProgress/create` request.

        The `window/workDoneProgress/create` request is sent from the server to the client to initiate progress
        reporting from the server.
        """
        return self.protocol.send_request("window/workDoneProgress/create", params, callback)

    async def window_work_done_progress_create_async(
        self,
        params: types.WorkDoneProgressCreateParams,
    ) -> None:
        """Make a :lsp:`window/workDoneProgress/create` request.

        The `window/workDoneProgress/create` request is sent from the server to the client to initiate progress
        reporting from the server.
        """
        return await self.protocol.send_request_async("window/workDoneProgress/create", params)

    def workspace_apply_edit(
        self,
        params: types.ApplyWorkspaceEditParams,
        callback: Optional[Callable[[types.ApplyWorkspaceEditResult], None]] = None,
    ) -> Future[types.ApplyWorkspaceEditResult]:
        """Make a :lsp:`workspace/applyEdit` request.

        A request sent from the server to the client to modified certain resources.
        """
        return self.protocol.send_request("workspace/applyEdit", params, callback)

    async def workspace_apply_edit_async(
        self,
        params: types.ApplyWorkspaceEditParams,
    ) -> types.ApplyWorkspaceEditResult:
        """Make a :lsp:`workspace/applyEdit` request.

        A request sent from the server to the client to modified certain resources.
        """
        return await self.protocol.send_request_async("workspace/applyEdit", params)

    def workspace_code_lens_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/codeLens/refresh` request.

        A request to refresh all code actions

        @since 3.16.0
        """
        return self.protocol.send_request("workspace/codeLens/refresh", params, callback)

    async def workspace_code_lens_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/codeLens/refresh` request.

        A request to refresh all code actions

        @since 3.16.0
        """
        return await self.protocol.send_request_async("workspace/codeLens/refresh", params)

    def workspace_configuration(
        self,
        params: types.ConfigurationParams,
        callback: Optional[Callable[[Sequence[Optional[Any]]], None]] = None,
    ) -> Future[Sequence[Optional[Any]]]:
        """Make a :lsp:`workspace/configuration` request.

        The 'workspace/configuration' request is sent from the server to the client to fetch a certain
        configuration setting.

        This pull model replaces the old push model were the client signaled configuration change via an
        event. If the server still needs to react to configuration changes (since the server caches the
        result of `workspace/configuration` requests) the server should register for an empty configuration
        change event and empty the cache if such an event is received.
        """
        return self.protocol.send_request("workspace/configuration", params, callback)

    async def workspace_configuration_async(
        self,
        params: types.ConfigurationParams,
    ) -> Sequence[Optional[Any]]:
        """Make a :lsp:`workspace/configuration` request.

        The 'workspace/configuration' request is sent from the server to the client to fetch a certain
        configuration setting.

        This pull model replaces the old push model were the client signaled configuration change via an
        event. If the server still needs to react to configuration changes (since the server caches the
        result of `workspace/configuration` requests) the server should register for an empty configuration
        change event and empty the cache if such an event is received.
        """
        return await self.protocol.send_request_async("workspace/configuration", params)

    def workspace_diagnostic_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/diagnostic/refresh` request.

        The diagnostic refresh request definition.

        @since 3.17.0
        """
        return self.protocol.send_request("workspace/diagnostic/refresh", params, callback)

    async def workspace_diagnostic_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/diagnostic/refresh` request.

        The diagnostic refresh request definition.

        @since 3.17.0
        """
        return await self.protocol.send_request_async("workspace/diagnostic/refresh", params)

    def workspace_folding_range_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/foldingRange/refresh` request.

        @since 3.18.0
        @proposed
        """
        return self.protocol.send_request("workspace/foldingRange/refresh", params, callback)

    async def workspace_folding_range_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/foldingRange/refresh` request.

        @since 3.18.0
        @proposed
        """
        return await self.protocol.send_request_async("workspace/foldingRange/refresh", params)

    def workspace_inlay_hint_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/inlayHint/refresh` request.

        @since 3.17.0
        """
        return self.protocol.send_request("workspace/inlayHint/refresh", params, callback)

    async def workspace_inlay_hint_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/inlayHint/refresh` request.

        @since 3.17.0
        """
        return await self.protocol.send_request_async("workspace/inlayHint/refresh", params)

    def workspace_inline_value_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/inlineValue/refresh` request.

        @since 3.17.0
        """
        return self.protocol.send_request("workspace/inlineValue/refresh", params, callback)

    async def workspace_inline_value_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/inlineValue/refresh` request.

        @since 3.17.0
        """
        return await self.protocol.send_request_async("workspace/inlineValue/refresh", params)

    def workspace_semantic_tokens_refresh(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/semanticTokens/refresh` request.

        @since 3.16.0
        """
        return self.protocol.send_request("workspace/semanticTokens/refresh", params, callback)

    async def workspace_semantic_tokens_refresh_async(
        self,
        params: None,
    ) -> None:
        """Make a :lsp:`workspace/semanticTokens/refresh` request.

        @since 3.16.0
        """
        return await self.protocol.send_request_async("workspace/semanticTokens/refresh", params)

    def workspace_text_document_content_refresh(
        self,
        params: types.TextDocumentContentRefreshParams,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future[None]:
        """Make a :lsp:`workspace/textDocumentContent/refresh` request.

        The `workspace/textDocumentContent` request is sent from the server to the client to refresh
        the content of a specific text document.

        @since 3.18.0
        @proposed
        """
        return self.protocol.send_request("workspace/textDocumentContent/refresh", params, callback)

    async def workspace_text_document_content_refresh_async(
        self,
        params: types.TextDocumentContentRefreshParams,
    ) -> None:
        """Make a :lsp:`workspace/textDocumentContent/refresh` request.

        The `workspace/textDocumentContent` request is sent from the server to the client to refresh
        the content of a specific text document.

        @since 3.18.0
        @proposed
        """
        return await self.protocol.send_request_async("workspace/textDocumentContent/refresh", params)

    def workspace_workspace_folders(
        self,
        params: None,
        callback: Optional[Callable[[Optional[Sequence[types.WorkspaceFolder]]], None]] = None,
    ) -> Future[Optional[Sequence[types.WorkspaceFolder]]]:
        """Make a :lsp:`workspace/workspaceFolders` request.

        The `workspace/workspaceFolders` is sent from the server to the client to fetch the open workspace folders.
        """
        return self.protocol.send_request("workspace/workspaceFolders", params, callback)

    async def workspace_workspace_folders_async(
        self,
        params: None,
    ) -> Optional[Sequence[types.WorkspaceFolder]]:
        """Make a :lsp:`workspace/workspaceFolders` request.

        The `workspace/workspaceFolders` is sent from the server to the client to fetch the open workspace folders.
        """
        return await self.protocol.send_request_async("workspace/workspaceFolders", params)

    def cancel_request(self, params: types.CancelParams) -> None:
        """Send a :lsp:`$/cancelRequest` notification.


        """
        self.protocol.notify("$/cancelRequest", params)

    def log_trace(self, params: types.LogTraceParams) -> None:
        """Send a :lsp:`$/logTrace` notification.


        """
        self.protocol.notify("$/logTrace", params)

    def progress(self, params: types.ProgressParams) -> None:
        """Send a :lsp:`$/progress` notification.


        """
        self.protocol.notify("$/progress", params)

    def telemetry_event(self, params: typing.Optional[typing.Any]) -> None:
        """Send a :lsp:`telemetry/event` notification.

        The telemetry event notification is sent from the server to the client to ask
        the client to log telemetry data.
        """
        self.protocol.notify("telemetry/event", params)

    def text_document_publish_diagnostics(self, params: types.PublishDiagnosticsParams) -> None:
        """Send a :lsp:`textDocument/publishDiagnostics` notification.

        Diagnostics notification are sent from the server to the client to signal
        results of validation runs.
        """
        self.protocol.notify("textDocument/publishDiagnostics", params)

    def window_log_message(self, params: types.LogMessageParams) -> None:
        """Send a :lsp:`window/logMessage` notification.

        The log message notification is sent from the server to the client to ask
        the client to log a particular message.
        """
        self.protocol.notify("window/logMessage", params)

    def window_show_message(self, params: types.ShowMessageParams) -> None:
        """Send a :lsp:`window/showMessage` notification.

        The show message notification is sent from a server to a client to ask
        the client to display a particular message in the user interface.
        """
        self.protocol.notify("window/showMessage", params)
