from __future__ import annotations

import typing

from lsprotocol import types

from pygls.exceptions import FeatureRequestError

from ._base_server import BaseLanguageServer

if typing.TYPE_CHECKING:
    from typing import Callable
    from typing import TypeVar

    from pygls.server import ServerErrors
    from pygls.progress import Progress
    from pygls.workspace import Workspace

    F = TypeVar("F", bound=Callable)


class LanguageServer(BaseLanguageServer):
    """The default LanguageServer

    This class can be extended and it can be passed as a first argument to
    registered commands/features.

    .. |ServerInfo| replace:: :class:`~lsprotocol.types.ServerInfo`

    Parameters
    ----------
    name
       Name of the server, used to populate |ServerInfo| which is sent to
       the client during initialization

    version
       Version of the server, used to populate |ServerInfo| which is sent to
       the client during initialization

    protocol_cls
       The :class:`~pygls.protocol.LanguageServerProtocol` class definition, or any
       subclass of it.

    max_workers
       Maximum number of workers for ``ThreadPool`` and ``ThreadPoolExecutor``

    text_document_sync_kind
       Text document synchronization method

       None
          No synchronization

       :attr:`~lsprotocol.types.TextDocumentSyncKind.Full`
          Send entire document text with each update

       :attr:`~lsprotocol.types.TextDocumentSyncKind.Incremental`
          Send only the region of text that changed with each update

    notebook_document_sync
       Advertise :lsp:`NotebookDocument` support to the client.
    """

    def __init__(
        self,
        name: str,
        version: str,
        text_document_sync_kind: types.TextDocumentSyncKind = types.TextDocumentSyncKind.Incremental,
        notebook_document_sync: types.NotebookDocumentSyncOptions | None = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.version = version
        self._text_document_sync_kind = text_document_sync_kind
        self._notebook_document_sync = notebook_document_sync
        self.process_id: int | None = None
        super().__init__(*args, **kwargs)

    @property
    def client_capabilities(self) -> types.ClientCapabilities:
        """The client's capabilities."""
        return self.protocol.client_capabilities

    @property
    def server_capabilities(self) -> types.ServerCapabilities:
        """The server's capabilities."""
        return self.protocol.server_capabilities

    @property
    def workspace(self) -> Workspace:
        """Returns in-memory workspace."""
        return self.protocol.workspace

    @property
    def work_done_progress(self) -> Progress:
        """Gets the object to manage client's progress bar."""
        return self.protocol.progress

    def report_server_error(self, error: Exception, source: ServerErrors):
        """
        Sends error to the client for displaying.

        By default this function does not handle LSP request errors. This is because LSP requests
        require direct responses and so already have a mechanism for including unexpected errors
        in the response body.

        All other errors are "out of band" in the sense that the client isn't explicitly waiting
        for them. For example diagnostics are returned as notifications, not responses to requests,
        and so can seemingly be sent at random. Also for example consider JSON RPC serialization
        and deserialization, if a payload cannot be parsed then the whole request/response cycle
        cannot be completed and so one of these "out of band" error messages is sent.

        These "out of band" error messages are not a requirement of the LSP spec. Pygls simply
        offers this behaviour as a recommended default. It is perfectly reasonble to override this
        default.
        """

        if source == FeatureRequestError:
            return

        self.window_show_message(
            types.ShowMessageParams(
                message=f"Error in server: {error}",
                type=types.MessageType.Error,
            )
        )
