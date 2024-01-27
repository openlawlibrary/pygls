# GENERATED FROM scripts/genenerate_base_lsp_classes.py -- DO NOT EDIT
# flake8: noqa
from __future__ import annotations

import typing

from pygls.server import JsonRPCServer

from .protocol import LanguageServerProtocol

if typing.TYPE_CHECKING:
    import asyncio
    from typing import Any, Callable, List, Optional, Type

    from lsprotocol import types

    from pygls.protocol import MsgId


class BaseLanguageServer(JsonRPCServer):
    """Base language server,"""

    def __init__(
        self,
        *args,
        protocol_cls: Type[LanguageServerProtocol] = LanguageServerProtocol,
        **kwargs,
    ):
        super().__init__(*args, protocol_cls=protocol_cls, **kwargs)

    def client_register_capability(
        self,
        params: types.RegistrationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`client/registerCapability` request.

        The `client/registerCapability` request is sent from the server to the client to register a new capability
        handler on the client side.
        """
        return self.send_request("client/registerCapability", params, msg_id=msg_id, callback=callback)

    def client_unregister_capability(
        self,
        params: types.UnregistrationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`client/unregisterCapability` request.

        The `client/unregisterCapability` request is sent from the server to the client to unregister a previously registered capability
        handler on the client side.
        """
        return self.send_request("client/unregisterCapability", params, msg_id=msg_id, callback=callback)

    def window_show_document(
        self,
        params: types.ShowDocumentParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.ShowDocumentResult], None]] = None,
    ) -> asyncio.Task[types.ShowDocumentResult]:
        """Make a :lsp:`window/showDocument` request.

        A request to show a document. This request might open an
        external program depending on the value of the URI to open.
        For example a request to open `https://code.visualstudio.com/`
        will very likely open the URI in a WEB browser.

        @since 3.16.0
        """
        return self.send_request("window/showDocument", params, msg_id=msg_id, callback=callback)

    def window_show_message_request(
        self,
        params: types.ShowMessageRequestParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.MessageActionItem]], None]] = None,
    ) -> asyncio.Task[Optional[types.MessageActionItem]]:
        """Make a :lsp:`window/showMessageRequest` request.

        The show message request is sent from the server to the client to show a message
        and a set of options actions to the user.
        """
        return self.send_request("window/showMessageRequest", params, msg_id=msg_id, callback=callback)

    def window_work_done_progress_create(
        self,
        params: types.WorkDoneProgressCreateParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`window/workDoneProgress/create` request.

        The `window/workDoneProgress/create` request is sent from the server to the client to initiate progress
        reporting from the server.
        """
        return self.send_request("window/workDoneProgress/create", params, msg_id=msg_id, callback=callback)

    def workspace_apply_edit(
        self,
        params: types.ApplyWorkspaceEditParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.ApplyWorkspaceEditResult], None]] = None,
    ) -> asyncio.Task[types.ApplyWorkspaceEditResult]:
        """Make a :lsp:`workspace/applyEdit` request.

        A request sent from the server to the client to modified certain resources.
        """
        return self.send_request("workspace/applyEdit", params, msg_id=msg_id, callback=callback)

    def workspace_code_lens_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/codeLens/refresh` request.

        A request to refresh all code actions

        @since 3.16.0
        """
        return self.send_request("workspace/codeLens/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_configuration(
        self,
        params: types.ConfigurationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[List[Optional[Any]]], None]] = None,
    ) -> asyncio.Task[List[Optional[Any]]]:
        """Make a :lsp:`workspace/configuration` request.

        The 'workspace/configuration' request is sent from the server to the client to fetch a certain
        configuration setting.

        This pull model replaces the old push model were the client signaled configuration change via an
        event. If the server still needs to react to configuration changes (since the server caches the
        result of `workspace/configuration` requests) the server should register for an empty configuration
        change event and empty the cache if such an event is received.
        """
        return self.send_request("workspace/configuration", params, msg_id=msg_id, callback=callback)

    def workspace_diagnostic_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/diagnostic/refresh` request.

        The diagnostic refresh request definition.

        @since 3.17.0
        """
        return self.send_request("workspace/diagnostic/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_folding_range_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/foldingRange/refresh` request.

        @since 3.18.0
        @proposed
        """
        return self.send_request("workspace/foldingRange/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_inlay_hint_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/inlayHint/refresh` request.

        @since 3.17.0
        """
        return self.send_request("workspace/inlayHint/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_inline_value_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/inlineValue/refresh` request.

        @since 3.17.0
        """
        return self.send_request("workspace/inlineValue/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_semantic_tokens_refresh(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`workspace/semanticTokens/refresh` request.

        @since 3.16.0
        """
        return self.send_request("workspace/semanticTokens/refresh", params, msg_id=msg_id, callback=callback)

    def workspace_workspace_folders(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.WorkspaceFolder]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.WorkspaceFolder]]]:
        """Make a :lsp:`workspace/workspaceFolders` request.

        The `workspace/workspaceFolders` is sent from the server to the client to fetch the open workspace folders.
        """
        return self.send_request("workspace/workspaceFolders", params, msg_id=msg_id, callback=callback)

    def cancel_request(self, params: types.CancelParams) -> None:
        """Send a :lsp:`$/cancelRequest` notification.


        """

        self.send_notification("$/cancelRequest", params)

    def log_trace(self, params: types.LogTraceParams) -> None:
        """Send a :lsp:`$/logTrace` notification.


        """

        self.send_notification("$/logTrace", params)

    def progress(self, params: types.ProgressParams) -> None:
        """Send a :lsp:`$/progress` notification.


        """

        self.send_notification("$/progress", params)

    def telemetry_event(self, params: Optional[Any]) -> None:
        """Send a :lsp:`telemetry/event` notification.

        The telemetry event notification is sent from the server to the client to ask
        the client to log telemetry data.
        """

        self.send_notification("telemetry/event", params)

    def text_document_publish_diagnostics(self, params: types.PublishDiagnosticsParams) -> None:
        """Send a :lsp:`textDocument/publishDiagnostics` notification.

        Diagnostics notification are sent from the server to the client to signal
        results of validation runs.
        """

        self.send_notification("textDocument/publishDiagnostics", params)

    def window_log_message(self, params: types.LogMessageParams) -> None:
        """Send a :lsp:`window/logMessage` notification.

        The log message notification is sent from the server to the client to ask
        the client to log a particular message.
        """

        self.send_notification("window/logMessage", params)

    def window_show_message(self, params: types.ShowMessageParams) -> None:
        """Send a :lsp:`window/showMessage` notification.

        The show message notification is sent from a server to a client to ask
        the client to display a particular message in the user interface.
        """

        self.send_notification("window/showMessage", params)
