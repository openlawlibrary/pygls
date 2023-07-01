# GENERATED FROM scripts/gen-client.py -- DO NOT EDIT
# flake8: noqa
from concurrent.futures import Future
from lsprotocol.types import CallHierarchyIncomingCall
from lsprotocol.types import CallHierarchyIncomingCallsParams
from lsprotocol.types import CallHierarchyItem
from lsprotocol.types import CallHierarchyOutgoingCall
from lsprotocol.types import CallHierarchyOutgoingCallsParams
from lsprotocol.types import CallHierarchyPrepareParams
from lsprotocol.types import CancelParams
from lsprotocol.types import CodeAction
from lsprotocol.types import CodeActionParams
from lsprotocol.types import CodeLens
from lsprotocol.types import CodeLensParams
from lsprotocol.types import ColorInformation
from lsprotocol.types import ColorPresentation
from lsprotocol.types import ColorPresentationParams
from lsprotocol.types import Command
from lsprotocol.types import CompletionItem
from lsprotocol.types import CompletionList
from lsprotocol.types import CompletionParams
from lsprotocol.types import CreateFilesParams
from lsprotocol.types import DeclarationParams
from lsprotocol.types import DefinitionParams
from lsprotocol.types import DeleteFilesParams
from lsprotocol.types import DidChangeConfigurationParams
from lsprotocol.types import DidChangeNotebookDocumentParams
from lsprotocol.types import DidChangeTextDocumentParams
from lsprotocol.types import DidChangeWatchedFilesParams
from lsprotocol.types import DidChangeWorkspaceFoldersParams
from lsprotocol.types import DidCloseNotebookDocumentParams
from lsprotocol.types import DidCloseTextDocumentParams
from lsprotocol.types import DidOpenNotebookDocumentParams
from lsprotocol.types import DidOpenTextDocumentParams
from lsprotocol.types import DidSaveNotebookDocumentParams
from lsprotocol.types import DidSaveTextDocumentParams
from lsprotocol.types import DocumentColorParams
from lsprotocol.types import DocumentDiagnosticParams
from lsprotocol.types import DocumentFormattingParams
from lsprotocol.types import DocumentHighlight
from lsprotocol.types import DocumentHighlightParams
from lsprotocol.types import DocumentLink
from lsprotocol.types import DocumentLinkParams
from lsprotocol.types import DocumentOnTypeFormattingParams
from lsprotocol.types import DocumentRangeFormattingParams
from lsprotocol.types import DocumentSymbol
from lsprotocol.types import DocumentSymbolParams
from lsprotocol.types import ExecuteCommandParams
from lsprotocol.types import FoldingRange
from lsprotocol.types import FoldingRangeParams
from lsprotocol.types import Hover
from lsprotocol.types import HoverParams
from lsprotocol.types import ImplementationParams
from lsprotocol.types import InitializeParams
from lsprotocol.types import InitializeResult
from lsprotocol.types import InitializedParams
from lsprotocol.types import InlayHint
from lsprotocol.types import InlayHintParams
from lsprotocol.types import InlineValueEvaluatableExpression
from lsprotocol.types import InlineValueParams
from lsprotocol.types import InlineValueText
from lsprotocol.types import InlineValueVariableLookup
from lsprotocol.types import LinkedEditingRangeParams
from lsprotocol.types import LinkedEditingRanges
from lsprotocol.types import Location
from lsprotocol.types import LocationLink
from lsprotocol.types import Moniker
from lsprotocol.types import MonikerParams
from lsprotocol.types import PrepareRenameParams
from lsprotocol.types import PrepareRenameResult_Type1
from lsprotocol.types import PrepareRenameResult_Type2
from lsprotocol.types import ProgressParams
from lsprotocol.types import Range
from lsprotocol.types import ReferenceParams
from lsprotocol.types import RelatedFullDocumentDiagnosticReport
from lsprotocol.types import RelatedUnchangedDocumentDiagnosticReport
from lsprotocol.types import RenameFilesParams
from lsprotocol.types import RenameParams
from lsprotocol.types import SelectionRange
from lsprotocol.types import SelectionRangeParams
from lsprotocol.types import SemanticTokens
from lsprotocol.types import SemanticTokensDelta
from lsprotocol.types import SemanticTokensDeltaParams
from lsprotocol.types import SemanticTokensParams
from lsprotocol.types import SemanticTokensRangeParams
from lsprotocol.types import SetTraceParams
from lsprotocol.types import SignatureHelp
from lsprotocol.types import SignatureHelpParams
from lsprotocol.types import SymbolInformation
from lsprotocol.types import TextEdit
from lsprotocol.types import TypeDefinitionParams
from lsprotocol.types import TypeHierarchyItem
from lsprotocol.types import TypeHierarchyPrepareParams
from lsprotocol.types import TypeHierarchySubtypesParams
from lsprotocol.types import TypeHierarchySupertypesParams
from lsprotocol.types import WillSaveTextDocumentParams
from lsprotocol.types import WorkDoneProgressCancelParams
from lsprotocol.types import WorkspaceDiagnosticParams
from lsprotocol.types import WorkspaceDiagnosticReport
from lsprotocol.types import WorkspaceEdit
from lsprotocol.types import WorkspaceSymbol
from lsprotocol.types import WorkspaceSymbolParams
from pygls.client import Client
from pygls.protocol import LanguageServerProtocol
from pygls.protocol import default_converter
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Union


class LanguageClient(Client):

    def __init__(
        self,
        name: str,
        version: str,
        protocol_cls=LanguageServerProtocol,
        converter_factory=default_converter,
        **kwargs,
    ):
        self.name = name
        self.version = version
        super().__init__(protocol_cls, converter_factory, **kwargs)

    def call_hierarchy_incoming_calls(
        self,
        params: CallHierarchyIncomingCallsParams,
        callback: Optional[Callable[[Optional[List[CallHierarchyIncomingCall]]], None]] = None,
    ) -> Future:
        """Make a ``callHierarchy/incomingCalls`` request.

        A request to resolve the incoming calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("callHierarchy/incomingCalls", params, callback)

    async def call_hierarchy_incoming_calls_async(
        self,
        params: CallHierarchyIncomingCallsParams,
    ) -> Optional[List[CallHierarchyIncomingCall]]:
        """Make a ``callHierarchy/incomingCalls`` request.

        A request to resolve the incoming calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("callHierarchy/incomingCalls", params)

    def call_hierarchy_outgoing_calls(
        self,
        params: CallHierarchyOutgoingCallsParams,
        callback: Optional[Callable[[Optional[List[CallHierarchyOutgoingCall]]], None]] = None,
    ) -> Future:
        """Make a ``callHierarchy/outgoingCalls`` request.

        A request to resolve the outgoing calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("callHierarchy/outgoingCalls", params, callback)

    async def call_hierarchy_outgoing_calls_async(
        self,
        params: CallHierarchyOutgoingCallsParams,
    ) -> Optional[List[CallHierarchyOutgoingCall]]:
        """Make a ``callHierarchy/outgoingCalls`` request.

        A request to resolve the outgoing calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("callHierarchy/outgoingCalls", params)

    def code_action_resolve(
        self,
        params: CodeAction,
        callback: Optional[Callable[[CodeAction], None]] = None,
    ) -> Future:
        """Make a ``codeAction/resolve`` request.

        Request to resolve additional information for a given code action.The request's
        parameter is of type {@link CodeAction} the response is of type {@link CodeAction}
        or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("codeAction/resolve", params, callback)

    async def code_action_resolve_async(
        self,
        params: CodeAction,
    ) -> CodeAction:
        """Make a ``codeAction/resolve`` request.

        Request to resolve additional information for a given code action.The request's
        parameter is of type {@link CodeAction} the response is of type {@link CodeAction}
        or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("codeAction/resolve", params)

    def code_lens_resolve(
        self,
        params: CodeLens,
        callback: Optional[Callable[[CodeLens], None]] = None,
    ) -> Future:
        """Make a ``codeLens/resolve`` request.

        A request to resolve a command for a given code lens.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("codeLens/resolve", params, callback)

    async def code_lens_resolve_async(
        self,
        params: CodeLens,
    ) -> CodeLens:
        """Make a ``codeLens/resolve`` request.

        A request to resolve a command for a given code lens.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("codeLens/resolve", params)

    def completion_item_resolve(
        self,
        params: CompletionItem,
        callback: Optional[Callable[[CompletionItem], None]] = None,
    ) -> Future:
        """Make a ``completionItem/resolve`` request.

        Request to resolve additional information for a given completion item.The
        request's parameter is of type {@link CompletionItem} the response is of type {@link
        CompletionItem} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("completionItem/resolve", params, callback)

    async def completion_item_resolve_async(
        self,
        params: CompletionItem,
    ) -> CompletionItem:
        """Make a ``completionItem/resolve`` request.

        Request to resolve additional information for a given completion item.The
        request's parameter is of type {@link CompletionItem} the response is of type {@link
        CompletionItem} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("completionItem/resolve", params)

    def document_link_resolve(
        self,
        params: DocumentLink,
        callback: Optional[Callable[[DocumentLink], None]] = None,
    ) -> Future:
        """Make a ``documentLink/resolve`` request.

        Request to resolve additional information for a given document link.

        The request's parameter is of type {@link DocumentLink} the response is of type
        {@link DocumentLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("documentLink/resolve", params, callback)

    async def document_link_resolve_async(
        self,
        params: DocumentLink,
    ) -> DocumentLink:
        """Make a ``documentLink/resolve`` request.

        Request to resolve additional information for a given document link.

        The request's parameter is of type {@link DocumentLink} the response is of type
        {@link DocumentLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("documentLink/resolve", params)

    def initialize(
        self,
        params: InitializeParams,
        callback: Optional[Callable[[InitializeResult], None]] = None,
    ) -> Future:
        """Make a ``initialize`` request.

        The initialize request is sent from the client to the server.

        It is sent once as the request after starting up the server. The requests parameter
        is of type {@link InitializeParams} the response if of type {@link InitializeResult}
        of a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("initialize", params, callback)

    async def initialize_async(
        self,
        params: InitializeParams,
    ) -> InitializeResult:
        """Make a ``initialize`` request.

        The initialize request is sent from the client to the server.

        It is sent once as the request after starting up the server. The requests parameter
        is of type {@link InitializeParams} the response if of type {@link InitializeResult}
        of a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("initialize", params)

    def inlay_hint_resolve(
        self,
        params: InlayHint,
        callback: Optional[Callable[[InlayHint], None]] = None,
    ) -> Future:
        """Make a ``inlayHint/resolve`` request.

        A request to resolve additional properties for an inlay hint. The request's
        parameter is of type {@link InlayHint}, the response is of type {@link InlayHint} or
        a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("inlayHint/resolve", params, callback)

    async def inlay_hint_resolve_async(
        self,
        params: InlayHint,
    ) -> InlayHint:
        """Make a ``inlayHint/resolve`` request.

        A request to resolve additional properties for an inlay hint. The request's
        parameter is of type {@link InlayHint}, the response is of type {@link InlayHint} or
        a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("inlayHint/resolve", params)

    def shutdown(
        self,
        params: None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> Future:
        """Make a ``shutdown`` request.

        A shutdown request is sent from the client to the server.

        It is sent once when the client decides to shutdown the server. The only
        notification that is sent after a shutdown request is the exit event.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("shutdown", params, callback)

    async def shutdown_async(
        self,
        params: None,
    ) -> None:
        """Make a ``shutdown`` request.

        A shutdown request is sent from the client to the server.

        It is sent once when the client decides to shutdown the server. The only
        notification that is sent after a shutdown request is the exit event.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("shutdown", params)

    def text_document_code_action(
        self,
        params: CodeActionParams,
        callback: Optional[Callable[[Optional[List[Union[Command, CodeAction]]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/codeAction`` request.

        A request to provide commands for the given text document and range.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/codeAction", params, callback)

    async def text_document_code_action_async(
        self,
        params: CodeActionParams,
    ) -> Optional[List[Union[Command, CodeAction]]]:
        """Make a ``textDocument/codeAction`` request.

        A request to provide commands for the given text document and range.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/codeAction", params)

    def text_document_code_lens(
        self,
        params: CodeLensParams,
        callback: Optional[Callable[[Optional[List[CodeLens]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/codeLens`` request.

        A request to provide code lens for the given text document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/codeLens", params, callback)

    async def text_document_code_lens_async(
        self,
        params: CodeLensParams,
    ) -> Optional[List[CodeLens]]:
        """Make a ``textDocument/codeLens`` request.

        A request to provide code lens for the given text document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/codeLens", params)

    def text_document_color_presentation(
        self,
        params: ColorPresentationParams,
        callback: Optional[Callable[[List[ColorPresentation]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/colorPresentation`` request.

        A request to list all presentation for a color.

        The request's parameter is of type {@link ColorPresentationParams} the response is
        of type {@link ColorInformation ColorInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/colorPresentation", params, callback)

    async def text_document_color_presentation_async(
        self,
        params: ColorPresentationParams,
    ) -> List[ColorPresentation]:
        """Make a ``textDocument/colorPresentation`` request.

        A request to list all presentation for a color.

        The request's parameter is of type {@link ColorPresentationParams} the response is
        of type {@link ColorInformation ColorInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/colorPresentation", params)

    def text_document_completion(
        self,
        params: CompletionParams,
        callback: Optional[Callable[[Union[List[CompletionItem], CompletionList, None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/completion`` request.

        Request to request completion at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response is of type {@link
        CompletionItem CompletionItem[]} or {@link CompletionList} or a Thenable that
        resolves to such.

        The request can delay the computation of the {@link CompletionItem.detail `detail`}
        and {@link CompletionItem.documentation `documentation`} properties to the
        `completionItem/resolve` request. However, properties that are needed for the
        initial sorting and filtering, like `sortText`, `filterText`, `insertText`, and
        `textEdit`, must not be changed during resolve.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/completion", params, callback)

    async def text_document_completion_async(
        self,
        params: CompletionParams,
    ) -> Union[List[CompletionItem], CompletionList, None]:
        """Make a ``textDocument/completion`` request.

        Request to request completion at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response is of type {@link
        CompletionItem CompletionItem[]} or {@link CompletionList} or a Thenable that
        resolves to such.

        The request can delay the computation of the {@link CompletionItem.detail `detail`}
        and {@link CompletionItem.documentation `documentation`} properties to the
        `completionItem/resolve` request. However, properties that are needed for the
        initial sorting and filtering, like `sortText`, `filterText`, `insertText`, and
        `textEdit`, must not be changed during resolve.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/completion", params)

    def text_document_declaration(
        self,
        params: DeclarationParams,
        callback: Optional[Callable[[Union[Location, List[Location], List[LocationLink], None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/declaration`` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Declaration} or a typed
        array of {@link DeclarationLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/declaration", params, callback)

    async def text_document_declaration_async(
        self,
        params: DeclarationParams,
    ) -> Union[Location, List[Location], List[LocationLink], None]:
        """Make a ``textDocument/declaration`` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Declaration} or a typed
        array of {@link DeclarationLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/declaration", params)

    def text_document_definition(
        self,
        params: DefinitionParams,
        callback: Optional[Callable[[Union[Location, List[Location], List[LocationLink], None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/definition`` request.

        A request to resolve the definition location of a symbol at a given text document
        position.

        The request's parameter is of type [TextDocumentPosition] (#TextDocumentPosition)
        the response is of either type {@link Definition} or a typed array of {@link
        DefinitionLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/definition", params, callback)

    async def text_document_definition_async(
        self,
        params: DefinitionParams,
    ) -> Union[Location, List[Location], List[LocationLink], None]:
        """Make a ``textDocument/definition`` request.

        A request to resolve the definition location of a symbol at a given text document
        position.

        The request's parameter is of type [TextDocumentPosition] (#TextDocumentPosition)
        the response is of either type {@link Definition} or a typed array of {@link
        DefinitionLink} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/definition", params)

    def text_document_diagnostic(
        self,
        params: DocumentDiagnosticParams,
        callback: Optional[Callable[[Union[RelatedFullDocumentDiagnosticReport, RelatedUnchangedDocumentDiagnosticReport]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/diagnostic`` request.

        The document diagnostic request definition.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/diagnostic", params, callback)

    async def text_document_diagnostic_async(
        self,
        params: DocumentDiagnosticParams,
    ) -> Union[RelatedFullDocumentDiagnosticReport, RelatedUnchangedDocumentDiagnosticReport]:
        """Make a ``textDocument/diagnostic`` request.

        The document diagnostic request definition.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/diagnostic", params)

    def text_document_document_color(
        self,
        params: DocumentColorParams,
        callback: Optional[Callable[[List[ColorInformation]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/documentColor`` request.

        A request to list all color symbols found in a given text document.

        The request's parameter is of type {@link DocumentColorParams} the response is of
        type {@link ColorInformation ColorInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/documentColor", params, callback)

    async def text_document_document_color_async(
        self,
        params: DocumentColorParams,
    ) -> List[ColorInformation]:
        """Make a ``textDocument/documentColor`` request.

        A request to list all color symbols found in a given text document.

        The request's parameter is of type {@link DocumentColorParams} the response is of
        type {@link ColorInformation ColorInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/documentColor", params)

    def text_document_document_highlight(
        self,
        params: DocumentHighlightParams,
        callback: Optional[Callable[[Optional[List[DocumentHighlight]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/documentHighlight`` request.

        Request to resolve a {@link DocumentHighlight} for a given text document
        position.

        The request's parameter is of type [TextDocumentPosition] (#TextDocumentPosition)
        the request response is of type [DocumentHighlight[]] (#DocumentHighlight) or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/documentHighlight", params, callback)

    async def text_document_document_highlight_async(
        self,
        params: DocumentHighlightParams,
    ) -> Optional[List[DocumentHighlight]]:
        """Make a ``textDocument/documentHighlight`` request.

        Request to resolve a {@link DocumentHighlight} for a given text document
        position.

        The request's parameter is of type [TextDocumentPosition] (#TextDocumentPosition)
        the request response is of type [DocumentHighlight[]] (#DocumentHighlight) or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/documentHighlight", params)

    def text_document_document_link(
        self,
        params: DocumentLinkParams,
        callback: Optional[Callable[[Optional[List[DocumentLink]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/documentLink`` request.

        A request to provide document links.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/documentLink", params, callback)

    async def text_document_document_link_async(
        self,
        params: DocumentLinkParams,
    ) -> Optional[List[DocumentLink]]:
        """Make a ``textDocument/documentLink`` request.

        A request to provide document links.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/documentLink", params)

    def text_document_document_symbol(
        self,
        params: DocumentSymbolParams,
        callback: Optional[Callable[[Union[List[SymbolInformation], List[DocumentSymbol], None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/documentSymbol`` request.

        A request to list all symbols found in a given text document.

        The request's parameter is of type {@link TextDocumentIdentifier} the response is of
        type {@link SymbolInformation SymbolInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/documentSymbol", params, callback)

    async def text_document_document_symbol_async(
        self,
        params: DocumentSymbolParams,
    ) -> Union[List[SymbolInformation], List[DocumentSymbol], None]:
        """Make a ``textDocument/documentSymbol`` request.

        A request to list all symbols found in a given text document.

        The request's parameter is of type {@link TextDocumentIdentifier} the response is of
        type {@link SymbolInformation SymbolInformation[]} or a Thenable that resolves to
        such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/documentSymbol", params)

    def text_document_folding_range(
        self,
        params: FoldingRangeParams,
        callback: Optional[Callable[[Optional[List[FoldingRange]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/foldingRange`` request.

        A request to provide folding ranges in a document.

        The request's parameter is of type {@link FoldingRangeParams}, the response is of
        type {@link FoldingRangeList} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/foldingRange", params, callback)

    async def text_document_folding_range_async(
        self,
        params: FoldingRangeParams,
    ) -> Optional[List[FoldingRange]]:
        """Make a ``textDocument/foldingRange`` request.

        A request to provide folding ranges in a document.

        The request's parameter is of type {@link FoldingRangeParams}, the response is of
        type {@link FoldingRangeList} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/foldingRange", params)

    def text_document_formatting(
        self,
        params: DocumentFormattingParams,
        callback: Optional[Callable[[Optional[List[TextEdit]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/formatting`` request.

        A request to format a whole document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/formatting", params, callback)

    async def text_document_formatting_async(
        self,
        params: DocumentFormattingParams,
    ) -> Optional[List[TextEdit]]:
        """Make a ``textDocument/formatting`` request.

        A request to format a whole document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/formatting", params)

    def text_document_hover(
        self,
        params: HoverParams,
        callback: Optional[Callable[[Optional[Hover]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/hover`` request.

        Request to request hover information at a given text document position.

        The request's parameter is of type {@link TextDocumentPosition} the response is of
        type {@link Hover} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/hover", params, callback)

    async def text_document_hover_async(
        self,
        params: HoverParams,
    ) -> Optional[Hover]:
        """Make a ``textDocument/hover`` request.

        Request to request hover information at a given text document position.

        The request's parameter is of type {@link TextDocumentPosition} the response is of
        type {@link Hover} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/hover", params)

    def text_document_implementation(
        self,
        params: ImplementationParams,
        callback: Optional[Callable[[Union[Location, List[Location], List[LocationLink], None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/implementation`` request.

        A request to resolve the implementation locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/implementation", params, callback)

    async def text_document_implementation_async(
        self,
        params: ImplementationParams,
    ) -> Union[Location, List[Location], List[LocationLink], None]:
        """Make a ``textDocument/implementation`` request.

        A request to resolve the implementation locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/implementation", params)

    def text_document_inlay_hint(
        self,
        params: InlayHintParams,
        callback: Optional[Callable[[Optional[List[InlayHint]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/inlayHint`` request.

        A request to provide inlay hints in a document. The request's parameter is of
        type {@link InlayHintsParams}, the response is of type {@link InlayHint InlayHint[]}
        or a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/inlayHint", params, callback)

    async def text_document_inlay_hint_async(
        self,
        params: InlayHintParams,
    ) -> Optional[List[InlayHint]]:
        """Make a ``textDocument/inlayHint`` request.

        A request to provide inlay hints in a document. The request's parameter is of
        type {@link InlayHintsParams}, the response is of type {@link InlayHint InlayHint[]}
        or a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/inlayHint", params)

    def text_document_inline_value(
        self,
        params: InlineValueParams,
        callback: Optional[Callable[[Optional[List[Union[InlineValueText, InlineValueVariableLookup, InlineValueEvaluatableExpression]]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/inlineValue`` request.

        A request to provide inline values in a document. The request's parameter is of
        type {@link InlineValueParams}, the response is of type {@link InlineValue
        InlineValue[]} or a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/inlineValue", params, callback)

    async def text_document_inline_value_async(
        self,
        params: InlineValueParams,
    ) -> Optional[List[Union[InlineValueText, InlineValueVariableLookup, InlineValueEvaluatableExpression]]]:
        """Make a ``textDocument/inlineValue`` request.

        A request to provide inline values in a document. The request's parameter is of
        type {@link InlineValueParams}, the response is of type {@link InlineValue
        InlineValue[]} or a Thenable that resolves to such.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/inlineValue", params)

    def text_document_linked_editing_range(
        self,
        params: LinkedEditingRangeParams,
        callback: Optional[Callable[[Optional[LinkedEditingRanges]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/linkedEditingRange`` request.

        A request to provide ranges that can be edited together.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/linkedEditingRange", params, callback)

    async def text_document_linked_editing_range_async(
        self,
        params: LinkedEditingRangeParams,
    ) -> Optional[LinkedEditingRanges]:
        """Make a ``textDocument/linkedEditingRange`` request.

        A request to provide ranges that can be edited together.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/linkedEditingRange", params)

    def text_document_moniker(
        self,
        params: MonikerParams,
        callback: Optional[Callable[[Optional[List[Moniker]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/moniker`` request.

        A request to get the moniker of a symbol at a given text document position.

        The request parameter is of type {@link TextDocumentPositionParams}. The response is
        of type {@link Moniker Moniker[]} or `null`.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/moniker", params, callback)

    async def text_document_moniker_async(
        self,
        params: MonikerParams,
    ) -> Optional[List[Moniker]]:
        """Make a ``textDocument/moniker`` request.

        A request to get the moniker of a symbol at a given text document position.

        The request parameter is of type {@link TextDocumentPositionParams}. The response is
        of type {@link Moniker Moniker[]} or `null`.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/moniker", params)

    def text_document_on_type_formatting(
        self,
        params: DocumentOnTypeFormattingParams,
        callback: Optional[Callable[[Optional[List[TextEdit]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/onTypeFormatting`` request.

        A request to format a document on type.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/onTypeFormatting", params, callback)

    async def text_document_on_type_formatting_async(
        self,
        params: DocumentOnTypeFormattingParams,
    ) -> Optional[List[TextEdit]]:
        """Make a ``textDocument/onTypeFormatting`` request.

        A request to format a document on type.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/onTypeFormatting", params)

    def text_document_prepare_call_hierarchy(
        self,
        params: CallHierarchyPrepareParams,
        callback: Optional[Callable[[Optional[List[CallHierarchyItem]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/prepareCallHierarchy`` request.

        A request to result a `CallHierarchyItem` in a document at a given position. Can
        be used as an input to an incoming or outgoing call hierarchy.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/prepareCallHierarchy", params, callback)

    async def text_document_prepare_call_hierarchy_async(
        self,
        params: CallHierarchyPrepareParams,
    ) -> Optional[List[CallHierarchyItem]]:
        """Make a ``textDocument/prepareCallHierarchy`` request.

        A request to result a `CallHierarchyItem` in a document at a given position. Can
        be used as an input to an incoming or outgoing call hierarchy.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/prepareCallHierarchy", params)

    def text_document_prepare_rename(
        self,
        params: PrepareRenameParams,
        callback: Optional[Callable[[Union[Range, PrepareRenameResult_Type1, PrepareRenameResult_Type2, None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/prepareRename`` request.

        A request to test and perform the setup necessary for a rename.

        @since 3.16 - support for default behavior
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/prepareRename", params, callback)

    async def text_document_prepare_rename_async(
        self,
        params: PrepareRenameParams,
    ) -> Union[Range, PrepareRenameResult_Type1, PrepareRenameResult_Type2, None]:
        """Make a ``textDocument/prepareRename`` request.

        A request to test and perform the setup necessary for a rename.

        @since 3.16 - support for default behavior
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/prepareRename", params)

    def text_document_prepare_type_hierarchy(
        self,
        params: TypeHierarchyPrepareParams,
        callback: Optional[Callable[[Optional[List[TypeHierarchyItem]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/prepareTypeHierarchy`` request.

        A request to result a `TypeHierarchyItem` in a document at a given position. Can
        be used as an input to a subtypes or supertypes type hierarchy.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/prepareTypeHierarchy", params, callback)

    async def text_document_prepare_type_hierarchy_async(
        self,
        params: TypeHierarchyPrepareParams,
    ) -> Optional[List[TypeHierarchyItem]]:
        """Make a ``textDocument/prepareTypeHierarchy`` request.

        A request to result a `TypeHierarchyItem` in a document at a given position. Can
        be used as an input to a subtypes or supertypes type hierarchy.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/prepareTypeHierarchy", params)

    def text_document_range_formatting(
        self,
        params: DocumentRangeFormattingParams,
        callback: Optional[Callable[[Optional[List[TextEdit]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/rangeFormatting`` request.

        A request to format a range in a document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/rangeFormatting", params, callback)

    async def text_document_range_formatting_async(
        self,
        params: DocumentRangeFormattingParams,
    ) -> Optional[List[TextEdit]]:
        """Make a ``textDocument/rangeFormatting`` request.

        A request to format a range in a document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/rangeFormatting", params)

    def text_document_references(
        self,
        params: ReferenceParams,
        callback: Optional[Callable[[Optional[List[Location]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/references`` request.

        A request to resolve project-wide references for the symbol denoted by the given
        text document position.

        The request's parameter is of type {@link ReferenceParams} the response is of type
        {@link Location Location[]} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/references", params, callback)

    async def text_document_references_async(
        self,
        params: ReferenceParams,
    ) -> Optional[List[Location]]:
        """Make a ``textDocument/references`` request.

        A request to resolve project-wide references for the symbol denoted by the given
        text document position.

        The request's parameter is of type {@link ReferenceParams} the response is of type
        {@link Location Location[]} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/references", params)

    def text_document_rename(
        self,
        params: RenameParams,
        callback: Optional[Callable[[Optional[WorkspaceEdit]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/rename`` request.

        A request to rename a symbol.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/rename", params, callback)

    async def text_document_rename_async(
        self,
        params: RenameParams,
    ) -> Optional[WorkspaceEdit]:
        """Make a ``textDocument/rename`` request.

        A request to rename a symbol.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/rename", params)

    def text_document_selection_range(
        self,
        params: SelectionRangeParams,
        callback: Optional[Callable[[Optional[List[SelectionRange]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/selectionRange`` request.

        A request to provide selection ranges in a document.

        The request's parameter is of type {@link SelectionRangeParams}, the response is of
        type {@link SelectionRange SelectionRange[]} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/selectionRange", params, callback)

    async def text_document_selection_range_async(
        self,
        params: SelectionRangeParams,
    ) -> Optional[List[SelectionRange]]:
        """Make a ``textDocument/selectionRange`` request.

        A request to provide selection ranges in a document.

        The request's parameter is of type {@link SelectionRangeParams}, the response is of
        type {@link SelectionRange SelectionRange[]} or a Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/selectionRange", params)

    def text_document_semantic_tokens_full(
        self,
        params: SemanticTokensParams,
        callback: Optional[Callable[[Optional[SemanticTokens]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/semanticTokens/full`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/semanticTokens/full", params, callback)

    async def text_document_semantic_tokens_full_async(
        self,
        params: SemanticTokensParams,
    ) -> Optional[SemanticTokens]:
        """Make a ``textDocument/semanticTokens/full`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/semanticTokens/full", params)

    def text_document_semantic_tokens_full_delta(
        self,
        params: SemanticTokensDeltaParams,
        callback: Optional[Callable[[Union[SemanticTokens, SemanticTokensDelta, None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/semanticTokens/full/delta`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/semanticTokens/full/delta", params, callback)

    async def text_document_semantic_tokens_full_delta_async(
        self,
        params: SemanticTokensDeltaParams,
    ) -> Union[SemanticTokens, SemanticTokensDelta, None]:
        """Make a ``textDocument/semanticTokens/full/delta`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/semanticTokens/full/delta", params)

    def text_document_semantic_tokens_range(
        self,
        params: SemanticTokensRangeParams,
        callback: Optional[Callable[[Optional[SemanticTokens]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/semanticTokens/range`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/semanticTokens/range", params, callback)

    async def text_document_semantic_tokens_range_async(
        self,
        params: SemanticTokensRangeParams,
    ) -> Optional[SemanticTokens]:
        """Make a ``textDocument/semanticTokens/range`` request.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/semanticTokens/range", params)

    def text_document_signature_help(
        self,
        params: SignatureHelpParams,
        callback: Optional[Callable[[Optional[SignatureHelp]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/signatureHelp`` request.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/signatureHelp", params, callback)

    async def text_document_signature_help_async(
        self,
        params: SignatureHelpParams,
    ) -> Optional[SignatureHelp]:
        """Make a ``textDocument/signatureHelp`` request.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/signatureHelp", params)

    def text_document_type_definition(
        self,
        params: TypeDefinitionParams,
        callback: Optional[Callable[[Union[Location, List[Location], List[LocationLink], None]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/typeDefinition`` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/typeDefinition", params, callback)

    async def text_document_type_definition_async(
        self,
        params: TypeDefinitionParams,
    ) -> Union[Location, List[Location], List[LocationLink], None]:
        """Make a ``textDocument/typeDefinition`` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position.

        The request's parameter is of type [TextDocumentPositionParams]
        (#TextDocumentPositionParams) the response is of type {@link Definition} or a
        Thenable that resolves to such.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/typeDefinition", params)

    def text_document_will_save_wait_until(
        self,
        params: WillSaveTextDocumentParams,
        callback: Optional[Callable[[Optional[List[TextEdit]]], None]] = None,
    ) -> Future:
        """Make a ``textDocument/willSaveWaitUntil`` request.

        A document will save request is sent from the client to the server before the
        document is actually saved.

        The request can return an array of TextEdits which will be applied to the text
        document before it is saved. Please note that clients might drop results if
        computing the text edits took too long or if a server constantly fails on this
        request. This is done to keep the save fast and reliable.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("textDocument/willSaveWaitUntil", params, callback)

    async def text_document_will_save_wait_until_async(
        self,
        params: WillSaveTextDocumentParams,
    ) -> Optional[List[TextEdit]]:
        """Make a ``textDocument/willSaveWaitUntil`` request.

        A document will save request is sent from the client to the server before the
        document is actually saved.

        The request can return an array of TextEdits which will be applied to the text
        document before it is saved. Please note that clients might drop results if
        computing the text edits took too long or if a server constantly fails on this
        request. This is done to keep the save fast and reliable.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("textDocument/willSaveWaitUntil", params)

    def type_hierarchy_subtypes(
        self,
        params: TypeHierarchySubtypesParams,
        callback: Optional[Callable[[Optional[List[TypeHierarchyItem]]], None]] = None,
    ) -> Future:
        """Make a ``typeHierarchy/subtypes`` request.

        A request to resolve the subtypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("typeHierarchy/subtypes", params, callback)

    async def type_hierarchy_subtypes_async(
        self,
        params: TypeHierarchySubtypesParams,
    ) -> Optional[List[TypeHierarchyItem]]:
        """Make a ``typeHierarchy/subtypes`` request.

        A request to resolve the subtypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("typeHierarchy/subtypes", params)

    def type_hierarchy_supertypes(
        self,
        params: TypeHierarchySupertypesParams,
        callback: Optional[Callable[[Optional[List[TypeHierarchyItem]]], None]] = None,
    ) -> Future:
        """Make a ``typeHierarchy/supertypes`` request.

        A request to resolve the supertypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("typeHierarchy/supertypes", params, callback)

    async def type_hierarchy_supertypes_async(
        self,
        params: TypeHierarchySupertypesParams,
    ) -> Optional[List[TypeHierarchyItem]]:
        """Make a ``typeHierarchy/supertypes`` request.

        A request to resolve the supertypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("typeHierarchy/supertypes", params)

    def workspace_diagnostic(
        self,
        params: WorkspaceDiagnosticParams,
        callback: Optional[Callable[[WorkspaceDiagnosticReport], None]] = None,
    ) -> Future:
        """Make a ``workspace/diagnostic`` request.

        The workspace diagnostic request definition.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/diagnostic", params, callback)

    async def workspace_diagnostic_async(
        self,
        params: WorkspaceDiagnosticParams,
    ) -> WorkspaceDiagnosticReport:
        """Make a ``workspace/diagnostic`` request.

        The workspace diagnostic request definition.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/diagnostic", params)

    def workspace_execute_command(
        self,
        params: ExecuteCommandParams,
        callback: Optional[Callable[[Optional[Any]], None]] = None,
    ) -> Future:
        """Make a ``workspace/executeCommand`` request.

        A request send from the client to the server to execute a command.

        The request might return a workspace edit which the client will apply to the
        workspace.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/executeCommand", params, callback)

    async def workspace_execute_command_async(
        self,
        params: ExecuteCommandParams,
    ) -> Optional[Any]:
        """Make a ``workspace/executeCommand`` request.

        A request send from the client to the server to execute a command.

        The request might return a workspace edit which the client will apply to the
        workspace.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/executeCommand", params)

    def workspace_symbol(
        self,
        params: WorkspaceSymbolParams,
        callback: Optional[Callable[[Union[List[SymbolInformation], List[WorkspaceSymbol], None]], None]] = None,
    ) -> Future:
        """Make a ``workspace/symbol`` request.

        A request to list project-wide symbols matching the query string given by the
        {@link WorkspaceSymbolParams}. The response is of type {@link SymbolInformation
        SymbolInformation[]} or a Thenable that resolves to such.

        @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
         need to advertise support for WorkspaceSymbols via the client capability
         `workspace.symbol.resolveSupport`.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/symbol", params, callback)

    async def workspace_symbol_async(
        self,
        params: WorkspaceSymbolParams,
    ) -> Union[List[SymbolInformation], List[WorkspaceSymbol], None]:
        """Make a ``workspace/symbol`` request.

        A request to list project-wide symbols matching the query string given by the
        {@link WorkspaceSymbolParams}. The response is of type {@link SymbolInformation
        SymbolInformation[]} or a Thenable that resolves to such.

        @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
         need to advertise support for WorkspaceSymbols via the client capability
         `workspace.symbol.resolveSupport`.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/symbol", params)

    def workspace_symbol_resolve(
        self,
        params: WorkspaceSymbol,
        callback: Optional[Callable[[WorkspaceSymbol], None]] = None,
    ) -> Future:
        """Make a ``workspaceSymbol/resolve`` request.

        A request to resolve the range inside the workspace symbol's location.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspaceSymbol/resolve", params, callback)

    async def workspace_symbol_resolve_async(
        self,
        params: WorkspaceSymbol,
    ) -> WorkspaceSymbol:
        """Make a ``workspaceSymbol/resolve`` request.

        A request to resolve the range inside the workspace symbol's location.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspaceSymbol/resolve", params)

    def workspace_will_create_files(
        self,
        params: CreateFilesParams,
        callback: Optional[Callable[[Optional[WorkspaceEdit]], None]] = None,
    ) -> Future:
        """Make a ``workspace/willCreateFiles`` request.

        The will create files request is sent from the client to the server before files
        are actually created as long as the creation is triggered from within the client.

        The request can return a `WorkspaceEdit` which will be applied to workspace before the
        files are created. Hence the `WorkspaceEdit` can not manipulate the content of the file
        to be created.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/willCreateFiles", params, callback)

    async def workspace_will_create_files_async(
        self,
        params: CreateFilesParams,
    ) -> Optional[WorkspaceEdit]:
        """Make a ``workspace/willCreateFiles`` request.

        The will create files request is sent from the client to the server before files
        are actually created as long as the creation is triggered from within the client.

        The request can return a `WorkspaceEdit` which will be applied to workspace before the
        files are created. Hence the `WorkspaceEdit` can not manipulate the content of the file
        to be created.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/willCreateFiles", params)

    def workspace_will_delete_files(
        self,
        params: DeleteFilesParams,
        callback: Optional[Callable[[Optional[WorkspaceEdit]], None]] = None,
    ) -> Future:
        """Make a ``workspace/willDeleteFiles`` request.

        The did delete files notification is sent from the client to the server when
        files were deleted from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/willDeleteFiles", params, callback)

    async def workspace_will_delete_files_async(
        self,
        params: DeleteFilesParams,
    ) -> Optional[WorkspaceEdit]:
        """Make a ``workspace/willDeleteFiles`` request.

        The did delete files notification is sent from the client to the server when
        files were deleted from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/willDeleteFiles", params)

    def workspace_will_rename_files(
        self,
        params: RenameFilesParams,
        callback: Optional[Callable[[Optional[WorkspaceEdit]], None]] = None,
    ) -> Future:
        """Make a ``workspace/willRenameFiles`` request.

        The will rename files request is sent from the client to the server before files
        are actually renamed as long as the rename is triggered from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return self.protocol.send_request("workspace/willRenameFiles", params, callback)

    async def workspace_will_rename_files_async(
        self,
        params: RenameFilesParams,
    ) -> Optional[WorkspaceEdit]:
        """Make a ``workspace/willRenameFiles`` request.

        The will rename files request is sent from the client to the server before files
        are actually renamed as long as the rename is triggered from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        return await self.protocol.send_request_async("workspace/willRenameFiles", params)

    def cancel_request(self, params: CancelParams) -> None:
        """Send a ``$/cancelRequest`` notification.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("$/cancelRequest", params)

    def exit(self, params: None) -> None:
        """Send a ``exit`` notification.

        The exit event is sent from the client to the server to ask the server to exit
        its process.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("exit", params)

    def initialized(self, params: InitializedParams) -> None:
        """Send a ``initialized`` notification.

        The initialized notification is sent from the client to the server after the
        client is fully initialized and the server is allowed to send requests from the
        server to the client.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("initialized", params)

    def notebook_document_did_change(self, params: DidChangeNotebookDocumentParams) -> None:
        """Send a ``notebookDocument/didChange`` notification.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("notebookDocument/didChange", params)

    def notebook_document_did_close(self, params: DidCloseNotebookDocumentParams) -> None:
        """Send a ``notebookDocument/didClose`` notification.

        A notification sent when a notebook closes.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("notebookDocument/didClose", params)

    def notebook_document_did_open(self, params: DidOpenNotebookDocumentParams) -> None:
        """Send a ``notebookDocument/didOpen`` notification.

        A notification sent when a notebook opens.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("notebookDocument/didOpen", params)

    def notebook_document_did_save(self, params: DidSaveNotebookDocumentParams) -> None:
        """Send a ``notebookDocument/didSave`` notification.

        A notification sent when a notebook document is saved.

        @since 3.17.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("notebookDocument/didSave", params)

    def progress(self, params: ProgressParams) -> None:
        """Send a ``$/progress`` notification.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("$/progress", params)

    def set_trace(self, params: SetTraceParams) -> None:
        """Send a ``$/setTrace`` notification.


        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("$/setTrace", params)

    def text_document_did_change(self, params: DidChangeTextDocumentParams) -> None:
        """Send a ``textDocument/didChange`` notification.

        The document change notification is sent from the client to the server to signal
        changes to a text document.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("textDocument/didChange", params)

    def text_document_did_close(self, params: DidCloseTextDocumentParams) -> None:
        """Send a ``textDocument/didClose`` notification.

        The document close notification is sent from the client to the server when the
        document got closed in the client.

        The document's truth now exists where the document's uri points to (e.g. if the
        document's uri is a file uri the truth now exists on disk). As with the open
        notification the close notification is about managing the document's content.
        Receiving a close notification doesn't mean that the document was open in an editor
        before. A close notification requires a previous open notification to be sent.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("textDocument/didClose", params)

    def text_document_did_open(self, params: DidOpenTextDocumentParams) -> None:
        """Send a ``textDocument/didOpen`` notification.

        The document open notification is sent from the client to the server to signal
        newly opened text documents.

        The document's truth is now managed by the client and the server must not try to
        read the document's truth using the document's uri. Open in this sense means it is
        managed by the client. It doesn't necessarily mean that its content is presented in
        an editor. An open notification must not be sent more than once without a
        corresponding close notification send before. This means open and close notification
        must be balanced and the max open count is one.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("textDocument/didOpen", params)

    def text_document_did_save(self, params: DidSaveTextDocumentParams) -> None:
        """Send a ``textDocument/didSave`` notification.

        The document save notification is sent from the client to the server when the
        document got saved in the client.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("textDocument/didSave", params)

    def text_document_will_save(self, params: WillSaveTextDocumentParams) -> None:
        """Send a ``textDocument/willSave`` notification.

        A document will save notification is sent from the client to the server before
        the document is actually saved.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("textDocument/willSave", params)

    def window_work_done_progress_cancel(self, params: WorkDoneProgressCancelParams) -> None:
        """Send a ``window/workDoneProgress/cancel`` notification.

        The `window/workDoneProgress/cancel` notification is sent from  the client to the
        server to cancel a progress initiated on the server side.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("window/workDoneProgress/cancel", params)

    def workspace_did_change_configuration(self, params: DidChangeConfigurationParams) -> None:
        """Send a ``workspace/didChangeConfiguration`` notification.

        The configuration change notification is sent from the client to the server when
        the client's configuration has changed.

        The notification contains the changed configuration as defined by the language
        client.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didChangeConfiguration", params)

    def workspace_did_change_watched_files(self, params: DidChangeWatchedFilesParams) -> None:
        """Send a ``workspace/didChangeWatchedFiles`` notification.

        The watched files notification is sent from the client to the server when the
        client detects changes to file watched by the language client.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didChangeWatchedFiles", params)

    def workspace_did_change_workspace_folders(self, params: DidChangeWorkspaceFoldersParams) -> None:
        """Send a ``workspace/didChangeWorkspaceFolders`` notification.

        The `workspace/didChangeWorkspaceFolders` notification is sent from the client to
        the server when the workspace folder configuration changes.
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didChangeWorkspaceFolders", params)

    def workspace_did_create_files(self, params: CreateFilesParams) -> None:
        """Send a ``workspace/didCreateFiles`` notification.

        The did create files notification is sent from the client to the server when
        files were created from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didCreateFiles", params)

    def workspace_did_delete_files(self, params: DeleteFilesParams) -> None:
        """Send a ``workspace/didDeleteFiles`` notification.

        The will delete files request is sent from the client to the server before files
        are actually deleted as long as the deletion is triggered from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didDeleteFiles", params)

    def workspace_did_rename_files(self, params: RenameFilesParams) -> None:
        """Send a ``workspace/didRenameFiles`` notification.

        The did rename files notification is sent from the client to the server when
        files were renamed from within the client.

        @since 3.16.0
        """
        if self.stopped:
            raise RuntimeError("Client has been stopped.")

        self.protocol.notify("workspace/didRenameFiles", params)
