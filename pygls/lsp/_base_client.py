# GENERATED FROM scripts/genenerate_base_lsp_classes.py -- DO NOT EDIT
# flake8: noqa
from __future__ import annotations

import typing

from pygls.client import JsonRPCClient

from .protocol import LanguageServerProtocol

if typing.TYPE_CHECKING:
    import asyncio
    from typing import Any, Callable, List, Optional, Type, Union

    from lsprotocol import types

    from pygls.protocol import MsgId


class BaseLanguageClient(JsonRPCClient):
    """Base language client."""

    def __init__(
        self,
        *args,
        protocol_cls: Type[LanguageServerProtocol] = LanguageServerProtocol,
        **kwargs,
    ):
        super().__init__(*args, protocol_cls=protocol_cls, **kwargs)

    def call_hierarchy_incoming_calls(
        self,
        params: types.CallHierarchyIncomingCallsParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.CallHierarchyIncomingCall]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.CallHierarchyIncomingCall]]]:
        """Make a :lsp:`callHierarchy/incomingCalls` request.

        A request to resolve the incoming calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        return self.send_request("callHierarchy/incomingCalls", params, msg_id=msg_id, callback=callback)

    def call_hierarchy_outgoing_calls(
        self,
        params: types.CallHierarchyOutgoingCallsParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.CallHierarchyOutgoingCall]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.CallHierarchyOutgoingCall]]]:
        """Make a :lsp:`callHierarchy/outgoingCalls` request.

        A request to resolve the outgoing calls for a given `CallHierarchyItem`.

        @since 3.16.0
        """
        return self.send_request("callHierarchy/outgoingCalls", params, msg_id=msg_id, callback=callback)

    def code_action_resolve(
        self,
        params: types.CodeAction,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.CodeAction], None]] = None,
    ) -> asyncio.Task[types.CodeAction]:
        """Make a :lsp:`codeAction/resolve` request.

        Request to resolve additional information for a given code action.The request's
        parameter is of type {@link CodeAction} the response
        is of type {@link CodeAction} or a Thenable that resolves to such.
        """
        return self.send_request("codeAction/resolve", params, msg_id=msg_id, callback=callback)

    def code_lens_resolve(
        self,
        params: types.CodeLens,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.CodeLens], None]] = None,
    ) -> asyncio.Task[types.CodeLens]:
        """Make a :lsp:`codeLens/resolve` request.

        A request to resolve a command for a given code lens.
        """
        return self.send_request("codeLens/resolve", params, msg_id=msg_id, callback=callback)

    def completion_item_resolve(
        self,
        params: types.CompletionItem,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.CompletionItem], None]] = None,
    ) -> asyncio.Task[types.CompletionItem]:
        """Make a :lsp:`completionItem/resolve` request.

        Request to resolve additional information for a given completion item.The request's
        parameter is of type {@link CompletionItem} the response
        is of type {@link CompletionItem} or a Thenable that resolves to such.
        """
        return self.send_request("completionItem/resolve", params, msg_id=msg_id, callback=callback)

    def document_link_resolve(
        self,
        params: types.DocumentLink,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.DocumentLink], None]] = None,
    ) -> asyncio.Task[types.DocumentLink]:
        """Make a :lsp:`documentLink/resolve` request.

        Request to resolve additional information for a given document link. The request's
        parameter is of type {@link DocumentLink} the response
        is of type {@link DocumentLink} or a Thenable that resolves to such.
        """
        return self.send_request("documentLink/resolve", params, msg_id=msg_id, callback=callback)

    def initialize(
        self,
        params: types.InitializeParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.InitializeResult], None]] = None,
    ) -> asyncio.Task[types.InitializeResult]:
        """Make a :lsp:`initialize` request.

        The initialize request is sent from the client to the server.
        It is sent once as the request after starting up the server.
        The requests parameter is of type {@link InitializeParams}
        the response if of type {@link InitializeResult} of a Thenable that
        resolves to such.
        """
        return self.send_request("initialize", params, msg_id=msg_id, callback=callback)

    def inlay_hint_resolve(
        self,
        params: types.InlayHint,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.InlayHint], None]] = None,
    ) -> asyncio.Task[types.InlayHint]:
        """Make a :lsp:`inlayHint/resolve` request.

        A request to resolve additional properties for an inlay hint.
        The request's parameter is of type {@link InlayHint}, the response is
        of type {@link InlayHint} or a Thenable that resolves to such.

        @since 3.17.0
        """
        return self.send_request("inlayHint/resolve", params, msg_id=msg_id, callback=callback)

    def shutdown(
        self,
        params: None,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[None], None]] = None,
    ) -> asyncio.Task[None]:
        """Make a :lsp:`shutdown` request.

        A shutdown request is sent from the client to the server.
        It is sent once when the client decides to shutdown the
        server. The only notification that is sent after a shutdown request
        is the exit event.
        """
        return self.send_request("shutdown", params, msg_id=msg_id, callback=callback)

    def text_document_code_action(
        self,
        params: types.CodeActionParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[Union[types.Command, types.CodeAction]]]], None]] = None,
    ) -> asyncio.Task[Optional[List[Union[types.Command, types.CodeAction]]]]:
        """Make a :lsp:`textDocument/codeAction` request.

        A request to provide commands for the given text document and range.
        """
        return self.send_request("textDocument/codeAction", params, msg_id=msg_id, callback=callback)

    def text_document_code_lens(
        self,
        params: types.CodeLensParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.CodeLens]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.CodeLens]]]:
        """Make a :lsp:`textDocument/codeLens` request.

        A request to provide code lens for the given text document.
        """
        return self.send_request("textDocument/codeLens", params, msg_id=msg_id, callback=callback)

    def text_document_color_presentation(
        self,
        params: types.ColorPresentationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[List[types.ColorPresentation]], None]] = None,
    ) -> asyncio.Task[List[types.ColorPresentation]]:
        """Make a :lsp:`textDocument/colorPresentation` request.

        A request to list all presentation for a color. The request's
        parameter is of type {@link ColorPresentationParams} the
        response is of type {@link ColorInformation ColorInformation[]} or a Thenable
        that resolves to such.
        """
        return self.send_request("textDocument/colorPresentation", params, msg_id=msg_id, callback=callback)

    def text_document_completion(
        self,
        params: types.CompletionParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[List[types.CompletionItem], types.CompletionList, None]], None]] = None,
    ) -> asyncio.Task[Union[List[types.CompletionItem], types.CompletionList, None]]:
        """Make a :lsp:`textDocument/completion` request.

        Request to request completion at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response
        is of type {@link CompletionItem CompletionItem[]} or {@link CompletionList}
        or a Thenable that resolves to such.

        The request can delay the computation of the {@link CompletionItem.detail `detail`}
        and {@link CompletionItem.documentation `documentation`} properties to the `completionItem/resolve`
        request. However, properties that are needed for the initial sorting and filtering, like `sortText`,
        `filterText`, `insertText`, and `textEdit`, must not be changed during resolve.
        """
        return self.send_request("textDocument/completion", params, msg_id=msg_id, callback=callback)

    def text_document_declaration(
        self,
        params: types.DeclarationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.Location, List[types.Location], List[types.LocationLink], None]], None]] = None,
    ) -> asyncio.Task[Union[types.Location, List[types.Location], List[types.LocationLink], None]]:
        """Make a :lsp:`textDocument/declaration` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type {@link TextDocumentPositionParams}
        the response is of type {@link Declaration} or a typed array of {@link DeclarationLink}
        or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/declaration", params, msg_id=msg_id, callback=callback)

    def text_document_definition(
        self,
        params: types.DefinitionParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.Location, List[types.Location], List[types.LocationLink], None]], None]] = None,
    ) -> asyncio.Task[Union[types.Location, List[types.Location], List[types.LocationLink], None]]:
        """Make a :lsp:`textDocument/definition` request.

        A request to resolve the definition location of a symbol at a given text
        document position. The request's parameter is of type {@link TextDocumentPosition}
        the response is of either type {@link Definition} or a typed array of
        {@link DefinitionLink} or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/definition", params, msg_id=msg_id, callback=callback)

    def text_document_diagnostic(
        self,
        params: types.DocumentDiagnosticParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.RelatedFullDocumentDiagnosticReport, types.RelatedUnchangedDocumentDiagnosticReport]], None]] = None,
    ) -> asyncio.Task[Union[types.RelatedFullDocumentDiagnosticReport, types.RelatedUnchangedDocumentDiagnosticReport]]:
        """Make a :lsp:`textDocument/diagnostic` request.

        The document diagnostic request definition.

        @since 3.17.0
        """
        return self.send_request("textDocument/diagnostic", params, msg_id=msg_id, callback=callback)

    def text_document_document_color(
        self,
        params: types.DocumentColorParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[List[types.ColorInformation]], None]] = None,
    ) -> asyncio.Task[List[types.ColorInformation]]:
        """Make a :lsp:`textDocument/documentColor` request.

        A request to list all color symbols found in a given text document. The request's
        parameter is of type {@link DocumentColorParams} the
        response is of type {@link ColorInformation ColorInformation[]} or a Thenable
        that resolves to such.
        """
        return self.send_request("textDocument/documentColor", params, msg_id=msg_id, callback=callback)

    def text_document_document_highlight(
        self,
        params: types.DocumentHighlightParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.DocumentHighlight]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.DocumentHighlight]]]:
        """Make a :lsp:`textDocument/documentHighlight` request.

        Request to resolve a {@link DocumentHighlight} for a given
        text document position. The request's parameter is of type {@link TextDocumentPosition}
        the request response is an array of type {@link DocumentHighlight}
        or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/documentHighlight", params, msg_id=msg_id, callback=callback)

    def text_document_document_link(
        self,
        params: types.DocumentLinkParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.DocumentLink]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.DocumentLink]]]:
        """Make a :lsp:`textDocument/documentLink` request.

        A request to provide document links
        """
        return self.send_request("textDocument/documentLink", params, msg_id=msg_id, callback=callback)

    def text_document_document_symbol(
        self,
        params: types.DocumentSymbolParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[List[types.SymbolInformation], List[types.DocumentSymbol], None]], None]] = None,
    ) -> asyncio.Task[Union[List[types.SymbolInformation], List[types.DocumentSymbol], None]]:
        """Make a :lsp:`textDocument/documentSymbol` request.

        A request to list all symbols found in a given text document. The request's
        parameter is of type {@link TextDocumentIdentifier} the
        response is of type {@link SymbolInformation SymbolInformation[]} or a Thenable
        that resolves to such.
        """
        return self.send_request("textDocument/documentSymbol", params, msg_id=msg_id, callback=callback)

    def text_document_folding_range(
        self,
        params: types.FoldingRangeParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.FoldingRange]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.FoldingRange]]]:
        """Make a :lsp:`textDocument/foldingRange` request.

        A request to provide folding ranges in a document. The request's
        parameter is of type {@link FoldingRangeParams}, the
        response is of type {@link FoldingRangeList} or a Thenable
        that resolves to such.
        """
        return self.send_request("textDocument/foldingRange", params, msg_id=msg_id, callback=callback)

    def text_document_formatting(
        self,
        params: types.DocumentFormattingParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TextEdit]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TextEdit]]]:
        """Make a :lsp:`textDocument/formatting` request.

        A request to format a whole document.
        """
        return self.send_request("textDocument/formatting", params, msg_id=msg_id, callback=callback)

    def text_document_hover(
        self,
        params: types.HoverParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.Hover]], None]] = None,
    ) -> asyncio.Task[Optional[types.Hover]]:
        """Make a :lsp:`textDocument/hover` request.

        Request to request hover information at a given text document position. The request's
        parameter is of type {@link TextDocumentPosition} the response is of
        type {@link Hover} or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/hover", params, msg_id=msg_id, callback=callback)

    def text_document_implementation(
        self,
        params: types.ImplementationParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.Location, List[types.Location], List[types.LocationLink], None]], None]] = None,
    ) -> asyncio.Task[Union[types.Location, List[types.Location], List[types.LocationLink], None]]:
        """Make a :lsp:`textDocument/implementation` request.

        A request to resolve the implementation locations of a symbol at a given text
        document position. The request's parameter is of type {@link TextDocumentPositionParams}
        the response is of type {@link Definition} or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/implementation", params, msg_id=msg_id, callback=callback)

    def text_document_inlay_hint(
        self,
        params: types.InlayHintParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.InlayHint]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.InlayHint]]]:
        """Make a :lsp:`textDocument/inlayHint` request.

        A request to provide inlay hints in a document. The request's parameter is of
        type {@link InlayHintsParams}, the response is of type
        {@link InlayHint InlayHint[]} or a Thenable that resolves to such.

        @since 3.17.0
        """
        return self.send_request("textDocument/inlayHint", params, msg_id=msg_id, callback=callback)

    def text_document_inline_completion(
        self,
        params: types.InlineCompletionParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.InlineCompletionList, List[types.InlineCompletionItem], None]], None]] = None,
    ) -> asyncio.Task[Union[types.InlineCompletionList, List[types.InlineCompletionItem], None]]:
        """Make a :lsp:`textDocument/inlineCompletion` request.

        A request to provide inline completions in a document. The request's parameter is of
        type {@link InlineCompletionParams}, the response is of type
        {@link InlineCompletion InlineCompletion[]} or a Thenable that resolves to such.

        @since 3.18.0
        @proposed
        """
        return self.send_request("textDocument/inlineCompletion", params, msg_id=msg_id, callback=callback)

    def text_document_inline_value(
        self,
        params: types.InlineValueParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[Union[types.InlineValueText, types.InlineValueVariableLookup, types.InlineValueEvaluatableExpression]]]], None]] = None,
    ) -> asyncio.Task[Optional[List[Union[types.InlineValueText, types.InlineValueVariableLookup, types.InlineValueEvaluatableExpression]]]]:
        """Make a :lsp:`textDocument/inlineValue` request.

        A request to provide inline values in a document. The request's parameter is of
        type {@link InlineValueParams}, the response is of type
        {@link InlineValue InlineValue[]} or a Thenable that resolves to such.

        @since 3.17.0
        """
        return self.send_request("textDocument/inlineValue", params, msg_id=msg_id, callback=callback)

    def text_document_linked_editing_range(
        self,
        params: types.LinkedEditingRangeParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.LinkedEditingRanges]], None]] = None,
    ) -> asyncio.Task[Optional[types.LinkedEditingRanges]]:
        """Make a :lsp:`textDocument/linkedEditingRange` request.

        A request to provide ranges that can be edited together.

        @since 3.16.0
        """
        return self.send_request("textDocument/linkedEditingRange", params, msg_id=msg_id, callback=callback)

    def text_document_moniker(
        self,
        params: types.MonikerParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.Moniker]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.Moniker]]]:
        """Make a :lsp:`textDocument/moniker` request.

        A request to get the moniker of a symbol at a given text document position.
        The request parameter is of type {@link TextDocumentPositionParams}.
        The response is of type {@link Moniker Moniker[]} or `null`.
        """
        return self.send_request("textDocument/moniker", params, msg_id=msg_id, callback=callback)

    def text_document_on_type_formatting(
        self,
        params: types.DocumentOnTypeFormattingParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TextEdit]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TextEdit]]]:
        """Make a :lsp:`textDocument/onTypeFormatting` request.

        A request to format a document on type.
        """
        return self.send_request("textDocument/onTypeFormatting", params, msg_id=msg_id, callback=callback)

    def text_document_prepare_call_hierarchy(
        self,
        params: types.CallHierarchyPrepareParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.CallHierarchyItem]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.CallHierarchyItem]]]:
        """Make a :lsp:`textDocument/prepareCallHierarchy` request.

        A request to result a `CallHierarchyItem` in a document at a given position.
        Can be used as an input to an incoming or outgoing call hierarchy.

        @since 3.16.0
        """
        return self.send_request("textDocument/prepareCallHierarchy", params, msg_id=msg_id, callback=callback)

    def text_document_prepare_rename(
        self,
        params: types.PrepareRenameParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.Range, types.PrepareRenameResult_Type1, types.PrepareRenameResult_Type2, None]], None]] = None,
    ) -> asyncio.Task[Union[types.Range, types.PrepareRenameResult_Type1, types.PrepareRenameResult_Type2, None]]:
        """Make a :lsp:`textDocument/prepareRename` request.

        A request to test and perform the setup necessary for a rename.

        @since 3.16 - support for default behavior
        """
        return self.send_request("textDocument/prepareRename", params, msg_id=msg_id, callback=callback)

    def text_document_prepare_type_hierarchy(
        self,
        params: types.TypeHierarchyPrepareParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TypeHierarchyItem]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TypeHierarchyItem]]]:
        """Make a :lsp:`textDocument/prepareTypeHierarchy` request.

        A request to result a `TypeHierarchyItem` in a document at a given position.
        Can be used as an input to a subtypes or supertypes type hierarchy.

        @since 3.17.0
        """
        return self.send_request("textDocument/prepareTypeHierarchy", params, msg_id=msg_id, callback=callback)

    def text_document_ranges_formatting(
        self,
        params: types.DocumentRangesFormattingParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TextEdit]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TextEdit]]]:
        """Make a :lsp:`textDocument/rangesFormatting` request.

        A request to format ranges in a document.

        @since 3.18.0
        @proposed
        """
        return self.send_request("textDocument/rangesFormatting", params, msg_id=msg_id, callback=callback)

    def text_document_range_formatting(
        self,
        params: types.DocumentRangeFormattingParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TextEdit]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TextEdit]]]:
        """Make a :lsp:`textDocument/rangeFormatting` request.

        A request to format a range in a document.
        """
        return self.send_request("textDocument/rangeFormatting", params, msg_id=msg_id, callback=callback)

    def text_document_references(
        self,
        params: types.ReferenceParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.Location]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.Location]]]:
        """Make a :lsp:`textDocument/references` request.

        A request to resolve project-wide references for the symbol denoted
        by the given text document position. The request's parameter is of
        type {@link ReferenceParams} the response is of type
        {@link Location Location[]} or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/references", params, msg_id=msg_id, callback=callback)

    def text_document_rename(
        self,
        params: types.RenameParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.WorkspaceEdit]], None]] = None,
    ) -> asyncio.Task[Optional[types.WorkspaceEdit]]:
        """Make a :lsp:`textDocument/rename` request.

        A request to rename a symbol.
        """
        return self.send_request("textDocument/rename", params, msg_id=msg_id, callback=callback)

    def text_document_selection_range(
        self,
        params: types.SelectionRangeParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.SelectionRange]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.SelectionRange]]]:
        """Make a :lsp:`textDocument/selectionRange` request.

        A request to provide selection ranges in a document. The request's
        parameter is of type {@link SelectionRangeParams}, the
        response is of type {@link SelectionRange SelectionRange[]} or a Thenable
        that resolves to such.
        """
        return self.send_request("textDocument/selectionRange", params, msg_id=msg_id, callback=callback)

    def text_document_semantic_tokens_full(
        self,
        params: types.SemanticTokensParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.SemanticTokens]], None]] = None,
    ) -> asyncio.Task[Optional[types.SemanticTokens]]:
        """Make a :lsp:`textDocument/semanticTokens/full` request.

        @since 3.16.0
        """
        return self.send_request("textDocument/semanticTokens/full", params, msg_id=msg_id, callback=callback)

    def text_document_semantic_tokens_full_delta(
        self,
        params: types.SemanticTokensDeltaParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.SemanticTokens, types.SemanticTokensDelta, None]], None]] = None,
    ) -> asyncio.Task[Union[types.SemanticTokens, types.SemanticTokensDelta, None]]:
        """Make a :lsp:`textDocument/semanticTokens/full/delta` request.

        @since 3.16.0
        """
        return self.send_request("textDocument/semanticTokens/full/delta", params, msg_id=msg_id, callback=callback)

    def text_document_semantic_tokens_range(
        self,
        params: types.SemanticTokensRangeParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.SemanticTokens]], None]] = None,
    ) -> asyncio.Task[Optional[types.SemanticTokens]]:
        """Make a :lsp:`textDocument/semanticTokens/range` request.

        @since 3.16.0
        """
        return self.send_request("textDocument/semanticTokens/range", params, msg_id=msg_id, callback=callback)

    def text_document_signature_help(
        self,
        params: types.SignatureHelpParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.SignatureHelp]], None]] = None,
    ) -> asyncio.Task[Optional[types.SignatureHelp]]:
        """Make a :lsp:`textDocument/signatureHelp` request.


        """
        return self.send_request("textDocument/signatureHelp", params, msg_id=msg_id, callback=callback)

    def text_document_type_definition(
        self,
        params: types.TypeDefinitionParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[types.Location, List[types.Location], List[types.LocationLink], None]], None]] = None,
    ) -> asyncio.Task[Union[types.Location, List[types.Location], List[types.LocationLink], None]]:
        """Make a :lsp:`textDocument/typeDefinition` request.

        A request to resolve the type definition locations of a symbol at a given text
        document position. The request's parameter is of type {@link TextDocumentPositionParams}
        the response is of type {@link Definition} or a Thenable that resolves to such.
        """
        return self.send_request("textDocument/typeDefinition", params, msg_id=msg_id, callback=callback)

    def text_document_will_save_wait_until(
        self,
        params: types.WillSaveTextDocumentParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TextEdit]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TextEdit]]]:
        """Make a :lsp:`textDocument/willSaveWaitUntil` request.

        A document will save request is sent from the client to the server before
        the document is actually saved. The request can return an array of TextEdits
        which will be applied to the text document before it is saved. Please note that
        clients might drop results if computing the text edits took too long or if a
        server constantly fails on this request. This is done to keep the save fast and
        reliable.
        """
        return self.send_request("textDocument/willSaveWaitUntil", params, msg_id=msg_id, callback=callback)

    def type_hierarchy_subtypes(
        self,
        params: types.TypeHierarchySubtypesParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TypeHierarchyItem]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TypeHierarchyItem]]]:
        """Make a :lsp:`typeHierarchy/subtypes` request.

        A request to resolve the subtypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        return self.send_request("typeHierarchy/subtypes", params, msg_id=msg_id, callback=callback)

    def type_hierarchy_supertypes(
        self,
        params: types.TypeHierarchySupertypesParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[List[types.TypeHierarchyItem]]], None]] = None,
    ) -> asyncio.Task[Optional[List[types.TypeHierarchyItem]]]:
        """Make a :lsp:`typeHierarchy/supertypes` request.

        A request to resolve the supertypes for a given `TypeHierarchyItem`.

        @since 3.17.0
        """
        return self.send_request("typeHierarchy/supertypes", params, msg_id=msg_id, callback=callback)

    def workspace_diagnostic(
        self,
        params: types.WorkspaceDiagnosticParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.WorkspaceDiagnosticReport], None]] = None,
    ) -> asyncio.Task[types.WorkspaceDiagnosticReport]:
        """Make a :lsp:`workspace/diagnostic` request.

        The workspace diagnostic request definition.

        @since 3.17.0
        """
        return self.send_request("workspace/diagnostic", params, msg_id=msg_id, callback=callback)

    def workspace_execute_command(
        self,
        params: types.ExecuteCommandParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[Any]], None]] = None,
    ) -> asyncio.Task[Optional[Any]]:
        """Make a :lsp:`workspace/executeCommand` request.

        A request send from the client to the server to execute a command. The request might return
        a workspace edit which the client will apply to the workspace.
        """
        return self.send_request("workspace/executeCommand", params, msg_id=msg_id, callback=callback)

    def workspace_symbol(
        self,
        params: types.WorkspaceSymbolParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Union[List[types.SymbolInformation], List[types.WorkspaceSymbol], None]], None]] = None,
    ) -> asyncio.Task[Union[List[types.SymbolInformation], List[types.WorkspaceSymbol], None]]:
        """Make a :lsp:`workspace/symbol` request.

        A request to list project-wide symbols matching the query string given
        by the {@link WorkspaceSymbolParams}. The response is
        of type {@link SymbolInformation SymbolInformation[]} or a Thenable that
        resolves to such.

        @since 3.17.0 - support for WorkspaceSymbol in the returned data. Clients
         need to advertise support for WorkspaceSymbols via the client capability
         `workspace.symbol.resolveSupport`.
        """
        return self.send_request("workspace/symbol", params, msg_id=msg_id, callback=callback)

    def workspace_symbol_resolve(
        self,
        params: types.WorkspaceSymbol,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[types.WorkspaceSymbol], None]] = None,
    ) -> asyncio.Task[types.WorkspaceSymbol]:
        """Make a :lsp:`workspaceSymbol/resolve` request.

        A request to resolve the range inside the workspace
        symbol's location.

        @since 3.17.0
        """
        return self.send_request("workspaceSymbol/resolve", params, msg_id=msg_id, callback=callback)

    def workspace_will_create_files(
        self,
        params: types.CreateFilesParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.WorkspaceEdit]], None]] = None,
    ) -> asyncio.Task[Optional[types.WorkspaceEdit]]:
        """Make a :lsp:`workspace/willCreateFiles` request.

        The will create files request is sent from the client to the server before files are actually
        created as long as the creation is triggered from within the client.

        The request can return a `WorkspaceEdit` which will be applied to workspace before the
        files are created. Hence the `WorkspaceEdit` can not manipulate the content of the file
        to be created.

        @since 3.16.0
        """
        return self.send_request("workspace/willCreateFiles", params, msg_id=msg_id, callback=callback)

    def workspace_will_delete_files(
        self,
        params: types.DeleteFilesParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.WorkspaceEdit]], None]] = None,
    ) -> asyncio.Task[Optional[types.WorkspaceEdit]]:
        """Make a :lsp:`workspace/willDeleteFiles` request.

        The did delete files notification is sent from the client to the server when
        files were deleted from within the client.

        @since 3.16.0
        """
        return self.send_request("workspace/willDeleteFiles", params, msg_id=msg_id, callback=callback)

    def workspace_will_rename_files(
        self,
        params: types.RenameFilesParams,
        msg_id: Optional[MsgId] = None,
        callback: Optional[Callable[[Optional[types.WorkspaceEdit]], None]] = None,
    ) -> asyncio.Task[Optional[types.WorkspaceEdit]]:
        """Make a :lsp:`workspace/willRenameFiles` request.

        The will rename files request is sent from the client to the server before files are actually
        renamed as long as the rename is triggered from within the client.

        @since 3.16.0
        """
        return self.send_request("workspace/willRenameFiles", params, msg_id=msg_id, callback=callback)

    def cancel_request(self, params: types.CancelParams) -> None:
        """Send a :lsp:`$/cancelRequest` notification.


        """

        self.send_notification("$/cancelRequest", params)

    def exit(self, params: None) -> None:
        """Send a :lsp:`exit` notification.

        The exit event is sent from the client to the server to
        ask the server to exit its process.
        """

        self.send_notification("exit", params)

    def initialized(self, params: types.InitializedParams) -> None:
        """Send a :lsp:`initialized` notification.

        The initialized notification is sent from the client to the
        server after the client is fully initialized and the server
        is allowed to send requests from the server to the client.
        """

        self.send_notification("initialized", params)

    def notebook_document_did_change(self, params: types.DidChangeNotebookDocumentParams) -> None:
        """Send a :lsp:`notebookDocument/didChange` notification.


        """

        self.send_notification("notebookDocument/didChange", params)

    def notebook_document_did_close(self, params: types.DidCloseNotebookDocumentParams) -> None:
        """Send a :lsp:`notebookDocument/didClose` notification.

        A notification sent when a notebook closes.

        @since 3.17.0
        """

        self.send_notification("notebookDocument/didClose", params)

    def notebook_document_did_open(self, params: types.DidOpenNotebookDocumentParams) -> None:
        """Send a :lsp:`notebookDocument/didOpen` notification.

        A notification sent when a notebook opens.

        @since 3.17.0
        """

        self.send_notification("notebookDocument/didOpen", params)

    def notebook_document_did_save(self, params: types.DidSaveNotebookDocumentParams) -> None:
        """Send a :lsp:`notebookDocument/didSave` notification.

        A notification sent when a notebook document is saved.

        @since 3.17.0
        """

        self.send_notification("notebookDocument/didSave", params)

    def progress(self, params: types.ProgressParams) -> None:
        """Send a :lsp:`$/progress` notification.


        """

        self.send_notification("$/progress", params)

    def set_trace(self, params: types.SetTraceParams) -> None:
        """Send a :lsp:`$/setTrace` notification.


        """

        self.send_notification("$/setTrace", params)

    def text_document_did_change(self, params: types.DidChangeTextDocumentParams) -> None:
        """Send a :lsp:`textDocument/didChange` notification.

        The document change notification is sent from the client to the server to signal
        changes to a text document.
        """

        self.send_notification("textDocument/didChange", params)

    def text_document_did_close(self, params: types.DidCloseTextDocumentParams) -> None:
        """Send a :lsp:`textDocument/didClose` notification.

        The document close notification is sent from the client to the server when
        the document got closed in the client. The document's truth now exists where
        the document's uri points to (e.g. if the document's uri is a file uri the
        truth now exists on disk). As with the open notification the close notification
        is about managing the document's content. Receiving a close notification
        doesn't mean that the document was open in an editor before. A close
        notification requires a previous open notification to be sent.
        """

        self.send_notification("textDocument/didClose", params)

    def text_document_did_open(self, params: types.DidOpenTextDocumentParams) -> None:
        """Send a :lsp:`textDocument/didOpen` notification.

        The document open notification is sent from the client to the server to signal
        newly opened text documents. The document's truth is now managed by the client
        and the server must not try to read the document's truth using the document's
        uri. Open in this sense means it is managed by the client. It doesn't necessarily
        mean that its content is presented in an editor. An open notification must not
        be sent more than once without a corresponding close notification send before.
        This means open and close notification must be balanced and the max open count
        is one.
        """

        self.send_notification("textDocument/didOpen", params)

    def text_document_did_save(self, params: types.DidSaveTextDocumentParams) -> None:
        """Send a :lsp:`textDocument/didSave` notification.

        The document save notification is sent from the client to the server when
        the document got saved in the client.
        """

        self.send_notification("textDocument/didSave", params)

    def text_document_will_save(self, params: types.WillSaveTextDocumentParams) -> None:
        """Send a :lsp:`textDocument/willSave` notification.

        A document will save notification is sent from the client to the server before
        the document is actually saved.
        """

        self.send_notification("textDocument/willSave", params)

    def window_work_done_progress_cancel(self, params: types.WorkDoneProgressCancelParams) -> None:
        """Send a :lsp:`window/workDoneProgress/cancel` notification.

        The `window/workDoneProgress/cancel` notification is sent from  the client to the server to cancel a progress
        initiated on the server side.
        """

        self.send_notification("window/workDoneProgress/cancel", params)

    def workspace_did_change_configuration(self, params: types.DidChangeConfigurationParams) -> None:
        """Send a :lsp:`workspace/didChangeConfiguration` notification.

        The configuration change notification is sent from the client to the server
        when the client's configuration has changed. The notification contains
        the changed configuration as defined by the language client.
        """

        self.send_notification("workspace/didChangeConfiguration", params)

    def workspace_did_change_watched_files(self, params: types.DidChangeWatchedFilesParams) -> None:
        """Send a :lsp:`workspace/didChangeWatchedFiles` notification.

        The watched files notification is sent from the client to the server when
        the client detects changes to file watched by the language client.
        """

        self.send_notification("workspace/didChangeWatchedFiles", params)

    def workspace_did_change_workspace_folders(self, params: types.DidChangeWorkspaceFoldersParams) -> None:
        """Send a :lsp:`workspace/didChangeWorkspaceFolders` notification.

        The `workspace/didChangeWorkspaceFolders` notification is sent from the client to the server when the workspace
        folder configuration changes.
        """

        self.send_notification("workspace/didChangeWorkspaceFolders", params)

    def workspace_did_create_files(self, params: types.CreateFilesParams) -> None:
        """Send a :lsp:`workspace/didCreateFiles` notification.

        The did create files notification is sent from the client to the server when
        files were created from within the client.

        @since 3.16.0
        """

        self.send_notification("workspace/didCreateFiles", params)

    def workspace_did_delete_files(self, params: types.DeleteFilesParams) -> None:
        """Send a :lsp:`workspace/didDeleteFiles` notification.

        The will delete files request is sent from the client to the server before files are actually
        deleted as long as the deletion is triggered from within the client.

        @since 3.16.0
        """

        self.send_notification("workspace/didDeleteFiles", params)

    def workspace_did_rename_files(self, params: types.RenameFilesParams) -> None:
        """Send a :lsp:`workspace/didRenameFiles` notification.

        The did rename files notification is sent from the client to the server when
        files were renamed from within the client.

        @since 3.16.0
        """

        self.send_notification("workspace/didRenameFiles", params)
