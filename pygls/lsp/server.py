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

import logging
import typing
from itertools import zip_longest

from lsprotocol import types

from pygls import uris
from pygls.exceptions import JsonRpcInvalidParams
from pygls.exceptions import JsonRpcMethodNotFound
from pygls.workspace import Workspace

from ._base_server import BaseLanguageServer
from .capabilities import ServerCapabilitiesBuilder

if typing.TYPE_CHECKING:
    from typing import Any
    from typing import Callable
    from typing import Dict
    from typing import Literal
    from typing import Optional
    from typing import Tuple
    from typing import TypeVar

    import cattrs

    F = TypeVar("F", bound=Callable)


logger = logging.getLogger(__name__)


def lsp_method(
    method_name: str,
    *,
    invoke_user_handler: Optional[Literal["before", "after"]] = None,
) -> Callable[[F], F]:
    """Define a builtin LSP method handler.

    Parameters
    ----------
    method_name
       The LSP method to register the handler for

    invoke_user_handler
       If set, this decorator will automatically take care of invoking the user's
       handler either ``before``, or ``after`` the builtin handler is executed.

       If ``None``, this either means the builtin method handles calling the user's
       handler itself, or intends to disallow the user's handler from running at all.

    """

    def decorator(f: F) -> F:
        if invoke_user_handler is None:
            f.method_name = method_name  # type: ignore[attr-defined]
            return f

        def builtin(self, *args, **kwargs):
            user_handler = self._features.user_features.get(method_name, None)
            if invoke_user_handler == "before" and user_handler is not None:
                yield user_handler, args, kwargs

            result = f(self, *args, **kwargs)

            if invoke_user_handler == "after" and user_handler is not None:
                yield user_handler, args, kwargs

            return result

        builtin.method_name = method_name
        return builtin

    return decorator


class LanguageServer(BaseLanguageServer):
    """Language Server."""

    def __init__(
        self,
        name: str,
        version: str,
        *args,
        text_document_sync_kind: types.TextDocumentSyncKind = types.TextDocumentSyncKind.Incremental,
        notebook_document_sync: Optional[types.NotebookDocumentSyncOptions] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.name = name
        self.version = version

        self._client_capabilities: Optional[types.ClientCapabilities] = None
        self._notebook_document_sync = notebook_document_sync
        self._text_document_sync_kind = text_document_sync_kind
        self._workspace: Optional[Workspace] = None
        self._register_builtin_features()

    def _register_builtin_features(self):
        """Registers builtin handlers for LSP features on this class."""
        for name in dir(self):
            # Trying to access these properties will throw runtime errors.
            if name in {"client_capabilities", "workspace", "writer"}:
                continue

            meth = getattr(self, name)
            if callable(meth) and hasattr(meth, "method_name"):
                self._features.add_builtin_feature(meth.method_name, meth)

    @property
    def client_capabilities(self) -> types.ClientCapabilities:
        if self._client_capabilities is None:
            raise RuntimeError(
                "The client's capabilities are not available - "
                "has the server been initialized?"
            )

        return self._client_capabilities

    @property
    def workspace(self) -> Workspace:
        if self._workspace is None:
            raise RuntimeError(
                "The workspace is not available - has the server been initialized?"
            )

        return self._workspace

    def command(self, command_name: str):
        """Decorator to register custom commands."""
        return self._features.command(self, command_name)

    @lsp_method(types.INITIALIZE)
    def lsp_initialize(self, params: types.InitializeParams) -> types.InitializeResult:
        """Method that initializes language server.
        It will compute and return server capabilities based on
        registered features.
        """
        # self._server.process_id = params.process_id
        root_path = params.root_path
        root_uri = params.root_uri
        if root_path is not None and root_uri is None:
            root_uri = uris.from_fs_path(root_path)

        # TODO: Call the user function (if provided) to give them chance to register
        # more features

        # Initialize server capabilities
        self._client_capabilities = params.capabilities
        self.server_capabilities = ServerCapabilitiesBuilder(
            self.client_capabilities,
            self._features,
            self._text_document_sync_kind,
            self._notebook_document_sync,
        ).build()

        # TODO: Move this step to before we yield to the user handler.
        # Initialize the workspace
        workspace_folders = params.workspace_folders or []
        self._workspace = Workspace(
            root_uri,
            self._text_document_sync_kind,
            workspace_folders,
            self.server_capabilities.position_encoding,
        )

        self.trace = types.TraceValues.Off

        return types.InitializeResult(
            capabilities=self.server_capabilities,
            server_info=types.InitializeResultServerInfoType(
                name=self.name, version=self.version
            ),
        )

    @lsp_method(types.INITIALIZED, invoke_user_handler="after")
    def __initialized(self, *args):
        """Notification received when client and server are connected."""
        # TODO: Register dynamic capabilities
        pass

    @lsp_method(types.SHUTDOWN, invoke_user_handler="before")
    def __shutdown(self, *args):
        """Request from client which asks server to shutdown."""

    @lsp_method(types.EXIT, invoke_user_handler="before")
    def lsp_exit(self, *args) -> None:
        """Stops the server process."""

    @lsp_method(types.TEXT_DOCUMENT_DID_CHANGE, invoke_user_handler="after")
    def __text_document__did_change(
        self, params: types.DidChangeTextDocumentParams
    ) -> None:
        """Updates document's content.
        (Incremental(from server capabilities); not configurable for now)
        """
        for change in params.content_changes:
            self.workspace.update_text_document(params.text_document, change)

    @lsp_method(types.TEXT_DOCUMENT_DID_CLOSE, invoke_user_handler="after")
    def __text_document__did_close(
        self, params: types.DidCloseTextDocumentParams
    ) -> None:
        """Removes document from workspace."""
        self.workspace.remove_text_document(params.text_document.uri)

    @lsp_method(types.TEXT_DOCUMENT_DID_OPEN, invoke_user_handler="after")
    def __text_document__did_open(
        self, params: types.DidOpenTextDocumentParams
    ) -> None:
        """Puts document to the workspace."""
        self.workspace.put_text_document(params.text_document)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_OPEN, invoke_user_handler="after")
    def __notebook_document__did_open(
        self, params: types.DidOpenNotebookDocumentParams
    ) -> None:
        """Put a notebook document into the workspace"""
        self.workspace.put_notebook_document(params)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CHANGE, invoke_user_handler="after")
    def __notebook_document__did_change(
        self, params: types.DidChangeNotebookDocumentParams
    ) -> None:
        """Update a notebook's contents"""
        self.workspace.update_notebook_document(params)

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CLOSE, invoke_user_handler="after")
    def __notebook_document__did_close(
        self, params: types.DidCloseNotebookDocumentParams
    ) -> None:
        """Remove a notebook document from the workspace."""
        self.workspace.remove_notebook_document(params)

    @lsp_method(types.SET_TRACE, invoke_user_handler="after")
    def __set_trace(self, params: types.SetTraceParams) -> None:
        """Changes server trace value."""
        self.trace = params.value

    @lsp_method(
        types.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS, invoke_user_handler="after"
    )
    def __workspace__did_change_workspace_folders(
        self, params: types.DidChangeWorkspaceFoldersParams
    ) -> None:
        """Adds/Removes folders from the workspace."""
        self.logger.info("Workspace folders changed: %s", params)

        added_folders = params.event.added or []
        removed_folders = params.event.removed or []

        for f_add, f_remove in zip_longest(added_folders, removed_folders):
            if f_add:
                self.workspace.add_folder(f_add)
            if f_remove:
                self.workspace.remove_folder(f_remove.uri)

    @lsp_method(types.WORKSPACE_EXECUTE_COMMAND)
    def __workspace__execute_command(self, params: types.ExecuteCommandParams):
        """Executes commands with passed arguments and returns a value."""
        if (handler := self._features.commands.get(params.command, None)) is None:
            raise JsonRpcMethodNotFound.of(params.command)

        try:
            args, kwargs = _prepare_command_arguments(handler, params, self.converter)
        except Exception as exc:
            raise JsonRpcInvalidParams.of(exc)

        # Call the user's command handler.
        result = yield handler, args, kwargs
        return result

    @lsp_method(types.WINDOW_WORK_DONE_PROGRESS_CANCEL)
    def __work_done_progress_cancel(
        self, params: types.WorkDoneProgressCancelParams
    ) -> None:
        """Received a progress cancellation from client."""
        # future = self.progress.tokens.get(params.token)
        # if future is None:
        #     logger.warning(
        #         "Ignoring work done progress cancel for unknown token %s", params.token
        #     )
        # else:
        #     future.cancel()


def _prepare_command_arguments(
    handler: Callable, params: types.ExecuteCommandParams, converter: cattrs.Converter
) -> Tuple[Tuple[Any], Dict[str, Any]]:
    """Prepare the arguments to pass to the command handler."""

    if params.arguments is None:
        return tuple(), {}

    arguments: Dict[str, Any] = {}

    try:
        annotations = typing.get_type_hints(handler)
    except TypeError:
        # If the user's handler requests the language server instance, the real function
        # is wrapped inside whatever `functools.partial()` returns.
        if not hasattr(handler, "func"):
            raise

        annotations = {
            k: v
            for k, v in typing.get_type_hints(handler.func).items()
            if not issubclass(v, LanguageServer)
        }

    # TODO: how to ensure argument order?!
    for value, (name, dtype) in zip_longest(params.arguments, annotations.items()):
        arguments[name] = converter.structure(value, dtype)

    return tuple(), arguments
