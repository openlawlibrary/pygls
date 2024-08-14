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
from __future__ import annotations

import json
import logging
import sys
import typing
from functools import lru_cache
from itertools import zip_longest
from typing import (
    Callable,
    Optional,
    Type,
    TypeVar,
)

from lsprotocol import types

from pygls.capabilities import ServerCapabilitiesBuilder
from pygls.protocol.json_rpc import JsonRPCProtocol
from pygls.protocol.lsp_meta import LSPMeta
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

if typing.TYPE_CHECKING:
    from cattrs import Converter

    from pygls.lsp.server import LanguageServer

F = TypeVar("F", bound=Callable)

logger = logging.getLogger(__name__)


def lsp_method(method_name: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f.method_name = method_name  # type: ignore[attr-defined]
        return f

    return decorator


class LanguageServerProtocol(JsonRPCProtocol, metaclass=LSPMeta):
    """A class that represents language server protocol.

    It contains implementations for generic LSP features.

    Attributes:
        workspace(Workspace): In memory workspace
    """

    _server: LanguageServer

    def __init__(self, server: LanguageServer, converter: Converter):
        super().__init__(server, converter)

        self._workspace: Optional[Workspace] = None
        self.trace = types.TraceValue.Off

        from pygls.progress import Progress

        self.progress = Progress(self)

        self.server_info = types.ServerInfo(
            name=server.name,
            version=server.version,
        )

        self._register_builtin_features()

    def _register_builtin_features(self):
        """Registers generic LSP features from this class."""
        for name in dir(self):
            if name in {"workspace"}:
                continue

            attr = getattr(self, name)
            if callable(attr) and hasattr(attr, "method_name"):
                self.fm.add_builtin_feature(attr.method_name, attr)

    @property
    def workspace(self) -> Workspace:
        if self._workspace is None:
            raise RuntimeError(
                "The workspace is not available - has the server been initialized?"
            )

        return self._workspace

    @lru_cache()
    def get_message_type(self, method: str) -> Optional[Type]:
        """Return LSP type definitions, as provided by `lsprotocol`"""
        return types.METHOD_TO_TYPES.get(method, (None,))[0]

    @lru_cache()
    def get_result_type(self, method: str) -> Optional[Type]:
        return types.METHOD_TO_TYPES.get(method, (None, None))[1]

    @lsp_method(types.EXIT)
    def lsp_exit(self, *args) -> None:
        """Stops the server process."""
        if self.transport is not None:
            self.transport.close()

        sys.exit(0 if self._shutdown else 1)

    @lsp_method(types.INITIALIZE)
    def lsp_initialize(self, params: types.InitializeParams) -> types.InitializeResult:
        """Method that initializes language server.
        It will compute and return server capabilities based on
        registered features.
        """
        logger.info("Language server initialized %s", params)

        self._server.process_id = params.process_id

        text_document_sync_kind = self._server._text_document_sync_kind
        notebook_document_sync = self._server._notebook_document_sync

        # Initialize server capabilities
        self.client_capabilities = params.capabilities
        self.server_capabilities = ServerCapabilitiesBuilder(
            self.client_capabilities,
            set({**self.fm.features, **self.fm.builtin_features}.keys()),
            self.fm.feature_options,
            list(self.fm.commands.keys()),
            text_document_sync_kind,
            notebook_document_sync,
        ).build()
        logger.debug(
            "Server capabilities: %s",
            json.dumps(self.server_capabilities, default=self._serialize_message),
        )

        root_path = params.root_path
        root_uri = params.root_uri
        if root_path is not None and root_uri is None:
            root_uri = from_fs_path(root_path)

        # Initialize the workspace
        workspace_folders = params.workspace_folders or []
        self._workspace = Workspace(
            root_uri,
            text_document_sync_kind,
            workspace_folders,
            self.server_capabilities.position_encoding,
        )

        return types.InitializeResult(
            capabilities=self.server_capabilities,
            server_info=self.server_info,
        )

    @lsp_method(types.INITIALIZED)
    def lsp_initialized(self, *args) -> None:
        """Notification received when client and server are connected."""
        pass

    @lsp_method(types.SHUTDOWN)
    def lsp_shutdown(self, *args) -> None:
        """Request from client which asks server to shutdown."""
        for future in self._request_futures.values():
            future.cancel()

        self._shutdown = True
        return None

    @lsp_method(types.TEXT_DOCUMENT_DID_CHANGE)
    def lsp_text_document__did_change(
        self, params: types.DidChangeTextDocumentParams
    ) -> None:
        """Updates document's content.
        (Incremental(from server capabilities); not configurable for now)
        """
        for change in params.content_changes:
            self.workspace.update_text_document(params.text_document, change)

    @lsp_method(types.TEXT_DOCUMENT_DID_CLOSE)
    def lsp_text_document__did_close(
        self, params: types.DidCloseTextDocumentParams
    ) -> None:
        """Removes document from workspace."""
        self.workspace.remove_text_document(params.text_document.uri)

    @lsp_method(types.TEXT_DOCUMENT_DID_OPEN)
    def lsp_text_document__did_open(
        self, params: types.DidOpenTextDocumentParams
    ) -> None:
        """Puts document to the workspace."""
        self.workspace.put_text_document(params.text_document)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_OPEN)
    def lsp_notebook_document__did_open(
        self, params: types.DidOpenNotebookDocumentParams
    ) -> None:
        """Put a notebook document into the workspace"""
        self.workspace.put_notebook_document(params)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CHANGE)
    def lsp_notebook_document__did_change(
        self, params: types.DidChangeNotebookDocumentParams
    ) -> None:
        """Update a notebook's contents"""
        self.workspace.update_notebook_document(params)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CLOSE)
    def lsp_notebook_document__did_close(
        self, params: types.DidCloseNotebookDocumentParams
    ) -> None:
        """Remove a notebook document from the workspace."""
        self.workspace.remove_notebook_document(params)

    @lsp_method(types.SET_TRACE)
    def lsp_set_trace(self, params: types.SetTraceParams) -> None:
        """Changes server trace value."""
        self.trace = params.value

    @lsp_method(types.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS)
    def lsp_workspace__did_change_workspace_folders(
        self, params: types.DidChangeWorkspaceFoldersParams
    ) -> None:
        """Adds/Removes folders from the workspace."""
        logger.info("Workspace folders changed: %s", params)

        added_folders = params.event.added or []
        removed_folders = params.event.removed or []

        for f_add, f_remove in zip_longest(added_folders, removed_folders):
            if f_add:
                self.workspace.add_folder(f_add)
            if f_remove:
                self.workspace.remove_folder(f_remove.uri)

    @lsp_method(types.WORKSPACE_EXECUTE_COMMAND)
    def lsp_workspace__execute_command(
        self, params: types.ExecuteCommandParams, msg_id: str
    ) -> None:
        """Executes commands with passed arguments and returns a value."""
        cmd_handler = self.fm.commands[params.command]
        self._execute_request(msg_id, cmd_handler, params.arguments)

    @lsp_method(types.WINDOW_WORK_DONE_PROGRESS_CANCEL)
    def lsp_work_done_progress_cancel(
        self, params: types.WorkDoneProgressCancelParams
    ) -> None:
        """Received a progress cancellation from client."""
        future = self.progress.tokens.get(params.token)
        if future is None:
            logger.warning(
                "Ignoring work done progress cancel for unknown token %s", params.token
            )
        else:
            future.cancel()
