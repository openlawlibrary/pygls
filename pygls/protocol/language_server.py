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

import asyncio
import inspect
import json
import logging
import sys
import typing
from functools import lru_cache
from itertools import zip_longest

from lsprotocol import types

from pygls.capabilities import ServerCapabilitiesBuilder
from pygls.constants import PARAM_LS
from pygls.exceptions import JsonRpcInvalidParams
from pygls.protocol.json_rpc import JsonRPCProtocol
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

if typing.TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any, Callable, Optional, Type, TypeVar

    from cattrs import Converter

    from pygls.lsp.server import LanguageServer

    F = TypeVar("F", bound=Callable)

logger = logging.getLogger(__name__)


def lsp_method(method_name: str) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        f.method_name = method_name  # type: ignore[attr-defined]
        return f

    return decorator


class LanguageServerProtocol(JsonRPCProtocol):
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
    def get_message_type(self, method: str) -> Type[Any] | None:
        """Return LSP type definitions, as provided by `lsprotocol`"""
        return types.METHOD_TO_TYPES.get(method, (None,))[0]

    @lru_cache()
    def get_result_type(self, method: str) -> Type[Any] | None:
        return types.METHOD_TO_TYPES.get(method, (None, None))[1]

    @lsp_method(types.EXIT)
    def lsp_exit(self, *args) -> Generator[Any, Any, None]:
        """Stops the server process."""

        # Ensure that the user handler is called first
        if (user_handler := self.fm.features.get(types.EXIT)) is not None:
            yield user_handler, args, None

        returncode = 0 if self._shutdown else 1
        if self.writer is None:
            sys.exit(returncode)

        res = self.writer.close()
        if inspect.isawaitable(res):
            # Only call sys.exit once the close task has completed.
            fut = asyncio.ensure_future(res)
            fut.add_done_callback(lambda t: sys.exit(returncode))
        else:
            sys.exit(returncode)

    @lsp_method(types.INITIALIZE)
    def lsp_initialize(
        self, params: types.InitializeParams
    ) -> Generator[Any, Any, types.InitializeResult]:
        """Method that initializes language server.
        It will compute and return server capabilities based on
        registered features.
        """
        logger.info("Language server initialized %s", params)

        self._server.process_id = params.process_id

        text_document_sync_kind = self._server._text_document_sync_kind
        notebook_document_sync = self._server._notebook_document_sync

        self.client_capabilities = params.capabilities
        position_encoding = ServerCapabilitiesBuilder.choose_position_encoding(
            self.client_capabilities
        )

        root_path = params.root_path
        root_uri = params.root_uri
        if root_path is not None and root_uri is None:
            root_uri = from_fs_path(root_path)

        # Initialize the workspace before yielding to the user's initialize handler
        workspace_folders = params.workspace_folders or []
        self._workspace = Workspace(
            root_uri,
            text_document_sync_kind,
            workspace_folders,
            position_encoding,
        )

        if (user_handler := self.fm.features.get(types.INITIALIZE)) is not None:
            yield user_handler, (params,), None

        # Now that the user has had the opportunity to setup additional features, calculate
        # the server's capabilities
        self.server_capabilities = ServerCapabilitiesBuilder(
            self.client_capabilities,
            set({**self.fm.features, **self.fm.builtin_features}.keys()),
            self.fm.feature_options,
            list(self.fm.commands.keys()),
            text_document_sync_kind,
            notebook_document_sync,
            position_encoding,
        ).build()
        logger.debug(
            "Server capabilities: %s",
            json.dumps(self.server_capabilities, default=self._serialize_message),
        )

        return types.InitializeResult(
            capabilities=self.server_capabilities,
            server_info=self.server_info,
        )

    @lsp_method(types.INITIALIZED)
    def lsp_initialized(self, *args):
        """Notification received when client and server are connected."""

        if (user_handler := self.fm.features.get(types.INITIALIZED)) is not None:
            yield user_handler, args, None

    @lsp_method(types.SHUTDOWN)
    def lsp_shutdown(self, *args) -> Generator[Any, Any, None]:
        """Request from client which asks server to shutdown."""

        if (user_handler := self.fm.features.get(types.SHUTDOWN)) is not None:
            yield user_handler, args, None

        # Don't cancel the future for this request!
        current_id = self.msg_id

        for msg_id, future in self._request_futures.items():
            if msg_id != current_id and not future.done():
                future.cancel()

        self._shutdown = True
        return None

    @lsp_method(types.TEXT_DOCUMENT_DID_CHANGE)
    def lsp_text_document__did_change(self, params: types.DidChangeTextDocumentParams):
        """Updates document's content.
        (Incremental(from server capabilities); not configurable for now)
        """
        for change in params.content_changes:
            self.workspace.update_text_document(params.text_document, change)

        if (
            user_handler := self.fm.features.get(types.TEXT_DOCUMENT_DID_CHANGE)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.TEXT_DOCUMENT_DID_CLOSE)
    def lsp_text_document__did_close(self, params: types.DidCloseTextDocumentParams):
        """Removes document from workspace."""
        self.workspace.remove_text_document(params.text_document.uri)

        if (
            user_handler := self.fm.features.get(types.TEXT_DOCUMENT_DID_CLOSE)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.TEXT_DOCUMENT_DID_OPEN)
    def lsp_text_document__did_open(self, params: types.DidOpenTextDocumentParams):
        """Puts document to the workspace."""
        self.workspace.put_text_document(params.text_document)

        if (
            user_handler := self.fm.features.get(types.TEXT_DOCUMENT_DID_OPEN)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_OPEN)
    def lsp_notebook_document__did_open(
        self, params: types.DidOpenNotebookDocumentParams
    ):
        """Put a notebook document into the workspace"""
        self.workspace.put_notebook_document(params)

        if (
            user_handler := self.fm.features.get(types.NOTEBOOK_DOCUMENT_DID_OPEN)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CHANGE)
    def lsp_notebook_document__did_change(
        self, params: types.DidChangeNotebookDocumentParams
    ):
        """Update a notebook's contents"""
        self.workspace.update_notebook_document(params)

        if (
            user_handler := self.fm.features.get(types.NOTEBOOK_DOCUMENT_DID_CHANGE)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.NOTEBOOK_DOCUMENT_DID_CLOSE)
    def lsp_notebook_document__did_close(
        self, params: types.DidCloseNotebookDocumentParams
    ):
        """Remove a notebook document from the workspace."""
        self.workspace.remove_notebook_document(params)

        if (
            user_handler := self.fm.features.get(types.NOTEBOOK_DOCUMENT_DID_CLOSE)
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.SET_TRACE)
    def lsp_set_trace(self, params: types.SetTraceParams) -> Generator[Any, Any, None]:
        """Changes server trace value."""
        self.trace = params.value

        if (user_handler := self.fm.features.get(types.SET_TRACE)) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS)
    def lsp_workspace__did_change_workspace_folders(
        self, params: types.DidChangeWorkspaceFoldersParams
    ):
        """Adds/Removes folders from the workspace."""
        logger.info("Workspace folders changed: %s", params)

        added_folders = params.event.added or []
        removed_folders = params.event.removed or []

        for f_add, f_remove in zip_longest(added_folders, removed_folders):
            if f_add:
                self.workspace.add_folder(f_add)
            if f_remove:
                self.workspace.remove_folder(f_remove.uri)

        if (
            user_handler := self.fm.features.get(
                types.WORKSPACE_DID_CHANGE_WORKSPACE_FOLDERS
            )
        ) is not None:
            yield user_handler, (params,), None

    @lsp_method(types.WORKSPACE_EXECUTE_COMMAND)
    def lsp_workspace__execute_command(
        self, params: types.ExecuteCommandParams
    ) -> Generator[Any, Any, Any]:
        """Executes commands with passed arguments and returns a value."""

        if (handler := self.fm.commands.get(params.command, None)) is None:
            raise JsonRpcInvalidParams.of(
                ValueError(f"Command name {params.command!r} is not defined")
            )

        try:
            args, kwargs = _prepare_command_arguments(handler, params, self._converter)
        except Exception as exc:
            raise JsonRpcInvalidParams.of(exc)

        # Call the user's command handler.
        result = yield handler, args, kwargs
        return result

    @lsp_method(types.WINDOW_WORK_DONE_PROGRESS_CANCEL)
    def lsp_work_done_progress_cancel(self, params: types.WorkDoneProgressCancelParams):
        """Received a progress cancellation from client."""
        future = self.progress.tokens.get(params.token)
        if future is None:
            logger.warning(
                "Ignoring work done progress cancel for unknown token %s", params.token
            )
        else:
            future.cancel()

        if (
            user_handler := self.fm.features.get(types.WINDOW_WORK_DONE_PROGRESS_CANCEL)
        ) is not None:
            yield user_handler, (params,), None


def _prepare_command_arguments(
    handler: Callable[..., Any],
    params: types.ExecuteCommandParams,
    converter: Converter,
) -> tuple[tuple[Any, ...], dict[str, Any]]:
    """Prepare the arguments to pass to the command handler."""

    if params.arguments is None:
        return tuple(), {}

    # Import this here to not introduce an import cycle at the module level
    from pygls.lsp.server import LanguageServer

    param_vals = iter(params.arguments)
    param_defs, annotations = _get_handler_params_annotations(handler)

    args: list[Any] = []
    kwargs: dict[str, Any] = {}

    # param_defs is an OrderedDict so *in theory* at least we don't have to
    # worry about argument order.
    found_ls = False
    for idx, (name, param) in enumerate(param_defs.items()):
        ptype = annotations.get(name, None)

        # We don't need to provide the injected server instance here.
        # The @server.command decorator will have already handled it.
        if idx == 0:
            if name == PARAM_LS:
                found_ls = True
                continue

            if (ptype is not None) and issubclass(ptype, LanguageServer):
                found_ls = True
                continue

        if param.kind == inspect.Parameter.VAR_POSITIONAL:  # i.e. *args
            # consume the remaining values
            args.extend(param_vals)

        else:
            try:
                value = converter.structure(next(param_vals), ptype)
            except StopIteration as exc:
                raise TypeError(
                    f"Expected {len(param_defs) - found_ls} arguments, "
                    f"got {len(params.arguments)}"
                ) from exc

            args.append(value)

    # did we consume all the values?
    if len(list(param_vals)) > 0:
        raise TypeError(
            f"Expected {len(param_defs) - found_ls} arguments, "
            f"got {len(params.arguments)}"
        )

    return tuple(args), kwargs


def _get_handler_params_annotations(handler: Callable[..., Any]):
    """Return the parameters and corresponding type annotations for the given handler
    function."""

    # If the user's handler requests the language server instance, the real function
    # is wrapped inside whatever `functools.partial()` returns.
    if hasattr(handler, "func"):
        annotations = typing.get_type_hints(handler.func)
        params = inspect.signature(handler.func).parameters

    else:
        annotations = typing.get_type_hints(handler)
        params = inspect.signature(handler).parameters

    return params, annotations
