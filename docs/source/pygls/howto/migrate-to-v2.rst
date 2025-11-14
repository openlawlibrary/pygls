How To Migrate to v2.0
======================

The highlight of the *pygls* v2 release is upgrading ``lsprotocol`` to ``v2025.x`` bringing with it support for the proposed LSP v3.18 types and methods.
The new version includes standardised object names (so no more classes like ``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType2CellsType``!)

With the major version bump, this release also takes the opportunity to clean up the codebase by removing deprecated code and renaming a few things to try and improve overall consistency.
This guide outlines how to adapt an existing server to the breaking changes introduced in this release.

**Known Migrations**

.. admonition:: Finished your migration?
   :class: tip

   Have you migrated your server to ``v2``?
   Feel free to open a pull request and add yours to the list below!

You may find these projects that have already successfully migrated to v2 a useful reference:

- Our `example servers <https://github.com/openlawlibrary/pygls/commit/e90f88ad642a20d3a16551e00a5a0abe0a1e041f>`__
- `pytest-lsp <https://github.com/swyddfa/lsp-devtools/pull/177>`__
- `esbonio <https://github.com/swyddfa/esbonio/pull/882>`__

Python Support
--------------

*pygls v2*

- Removes support for Python 3.8
- Adds support for Python 3.13 and 3.14 (with the GIL, you are welcome to try a free-threaded build just note that it has not been tested yet!)

URI Handling
------------

The :func:`pygls.uris.to_fs_path` will now return ``None`` for URIs that do not have a ``file:`` scheme.


Removed Deprecated Functions
----------------------------

The following methods and functions have been deprecated for some time and have now been removed in *pygls v2*.

==================================================  ==============
**pygls v1**                                        **pygls v2**
==================================================  ==============
``pygls.workspace.Document``                        ``pygls.workspace.TextDocument``
``pygls.workspace.utf16_unit_offset``               ``TextDocument.position_codec.utf16_unit_offset`` or ``Workspace.position_codec.utf16_unit_offset``
``pygls.workspace.utf16_num_units``                 ``TextDocument.position_codec.client_num_units`` or ``Workspace.position_codec.client_num_units``
``pygls.workspace.position_from_utf16``             ``TextDocument.position_codec.position_from_client_units`` or ``Workspace.position_codec.position_from_client_units``
``pygls.workspace.position_to_utf16``               ``TextDocument.position_codec.position_to_client_units`` or ``Workspace.position_codec.position_to_client_units``
``pygls.workspace.range_from_utf16``                ``TextDocument.position_codec.range_from_client_units`` or ``Workspace.position_codec.range_from_client_units``
``pygls.workspace.range_to_utf16``                  ``TextDocument.position_codec.range_to_client_units`` or ``Workspace.position_codec.range_to_client_units``
``Workspace.documents``                             ``Workspace.text_documents``
``Workspace.get_document``                           ``Workspace.get_text_document``
``Workspace.put_document``                           ``Workspace.put_text_document``
``Workspace.remove_document``                        ``Workspace.remove_text_document``
``Workspace.update_document``                        ``Workspace.update_text_document``
==================================================  ==============

Sending Custom Notifications
----------------------------

The ``send_notification`` method on the ``LanguageServer`` has been removed without a prior deprecation notice (sorry!)

To send custom notifications in v2, use the ``notify`` method on the underlying protocol object.

.. code-block:: python

   # Before
   server.send_notification("my/customNotification", {"example": "data"})

   # After
   server.protocol.notify("my/customNotification", {"example": "data"})

See :ref:`howto-send-custom-messages` for more details


Server commands are now called with individual arguments and can use type annotations
-------------------------------------------------------------------------------------

Instead of calling sever commands with a single arguments of type list containing all the command arguments, *pygls v2* now unpacks the arguments and passes them as individual parameters to the command method.

*pygls* will now inspect a function's type annotations when handling ``workspace/executeCommand`` requests, automatically converting JSON values to ``attrs`` class instances, or responding with an error if appropriate.

It is **not mandatory** to start using type annotations in your command definitions, but you will notice a difference in how *pygls* calls your server command methods if they take arguments.

**Before**

::

   @server.command("codeLens.evaluateSum")
   def evaluate_sum(ls: LanguageServer, args):
       logging.info("arguments: %s", args)  # here args is a list of dict

       arguments = args[0]
       document = ls.workspace.get_text_document(arguments["uri"])
       line = document.lines[arguments["line"]]

       # Compute the edit that will update the document with the result.
       answer = arguments["left"] + arguments["right"]
       edit = types.TextDocumentEdit(
           text_document=types.OptionalVersionedTextDocumentIdentifier(
               uri=arguments["uri"],
               version=document.version,
           ),
           edits=[
               types.TextEdit(
                   new_text=f"{line.strip()} {answer}\n",
                   range=types.Range(
                       start=types.Position(line=arguments["line"], character=0),
                       end=types.Position(line=arguments["line"] + 1, character=0),
                   ),
               )
           ],
       )

       # Apply the edit.
       ls.workspace_apply_edit(
           types.ApplyWorkspaceEditParams(
               edit=types.WorkspaceEdit(document_changes=[edit]),
           ),
       )

**After**

::

    @attrs.define
    class EvaluateSumArgs:
        """Represents the arguments to pass to the ``codeLens.evaluateSum`` command"""

        uri: str
        """The uri of the document to edit"""

        left: int
        """The left argument to ``+``"""

        right: int
        """The right argument to ``+``"""

        line: int
        """The line number to edit"""


    @server.command("codeLens.evaluateSum")
    def evaluate_sum(ls: LanguageServer, args: EvaluateSumArgs):
        logging.info("arguments: %s", args)  # here args is an instance of EvaluateSumArgs

        document = ls.workspace.get_text_document(args.uri)
        line = document.lines[args.line]

        # Compute the edit that will update the document with the result.
        answer = args.left + args.right
        edit = types.TextDocumentEdit(
            text_document=types.OptionalVersionedTextDocumentIdentifier(
                uri=args.uri,
                version=document.version,
            ),
            edits=[
                types.TextEdit(
                    new_text=f"{line.strip()} {answer}\n",
                    range=types.Range(
                        start=types.Position(line=args.line, character=0),
                        end=types.Position(line=args.line + 1, character=0),
                    ),
                )
            ],
        )

        # Apply the edit.
        ls.workspace_apply_edit(
            types.ApplyWorkspaceEditParams(
                edit=types.WorkspaceEdit(document_changes=[edit]),
            ),
        )




Renamed ``LanguageServer`` Methods
----------------------------------

The :class:`~pygls.lsp.server.LanuageServer` class has been moved to the ``pygls.lsp`` module::

   # Before
   from pygls.server import LanguageServer
   server = LanguageServer(name="my-language-server", version="v1.0")

   # After
   from pygls.lsp.server import LanguageServer
   server = LanguageServer(name="my-language-server", version="v1.0")

All LSP requests and notifications that can be sent by a server are now automatically generated from the specification, as a result the following methods have been renamed

==================================================  ==============
**pygls v1**                                        **pygls v2**
==================================================  ==============
``LanguageServer.apply_edit``                       ``LanguageServer.workspace_apply_edit``
``LanguageServer.apply_edit_async``                 ``LanguageServer.workspace_apply_edit_async``
``LanguageServer.get_configuration``                ``LanguageServer.workspace_configuration``
``LanguageServer.get_configuration_async``          ``LanguageServer.workspace_configuration_async``
``LanguageServer.publish_diagnostics``              ``LanguageServer.text_document_publish_diagnostics``
``LanguageServer.register_capability``              ``LanguageServer.client_register_capability``
``LanguageServer.register_capability_async``        ``LanguageServer.client_register_capability_async``
``LanguageServer.semantic_tokens_refresh``          ``LanguageServer.workspace_semantic_tokens_refresh``
``LanguageServer.semantic_tokens_refresh_async``    ``LanguageServer.workspace_semantic_tokens_refresh_async``
``LanguageServer.show_document``                    ``LanguageServer.window_show_document``
``LanguageServer.show_document_async``              ``LanguageServer.window_show_document_async``
``LanguageServer.show_message``                     ``LanguageServer.window_show_message``
``LanguageServer.show_message_log``                 ``LanguageServer.window_log_message``
``LanguageServer.unregister_capability``            ``LanguageServer.client_unregister_capability``
``LanguageServer.unregister_capability_async``      ``LanguageServer.client_unregister_capability_async``
==================================================  ==============

Additionally all LSP method signatures now require an instance of the corresponding ``params`` object for the method.
For example::

   # Before
   from pygls.server import LanguageServer

   server = LanguageServer(name="my-language-server", version="v1.0")
   server.publish_diagnostics(uri='...', diagnostics=[...])

   # After
   from lsprotocol import types
   from pygls.lsp.server import LanguageServer

   server = LanguageServer(name="my-language-server", version="v1.0")
   server.text_document_publish_diagnostics(
       types.PublishDiagnosticsParams(
           uri='...',
           diagnostics=[...],
       )
   )

Renamed ``LanguageServer.progress``
-----------------------------------

A consequence of the automatic method generation ``LanguageServer.progress`` now sends a ``$/progress`` notification, rather than giving access to pygls' :class:`~pygls.progress.Progress` helper.

The helper is now accessed via ``LanguageServer.work_done_progress``

**Before**

::

   from lsprotocol import types
   from pygls.server import LanguageServer

   server = LanguageServer(name="my-language-server", version="v1.0")

   @server.command('progress.example')
   async def progress(ls: LanguageServer, *args):
       """Create and start the progress on the client."""
       token = str(uuid.uuid4())
       # Create
       await ls.progress.create_async(token)
       # Begin
       ls.progress.begin(
           token,
           types.WorkDoneProgressBegin(title="Indexing", percentage=0, cancellable=True),
       )
       # Report
       for i in range(1, 10):
           # Check for cancellation from client
           if ls.progress.tokens[token].cancelled():
               # ... and stop the computation if client cancelled
               return
           ls.progress.report(
               token,
               types.WorkDoneProgressReport(message=f"{i * 10}%", percentage=i * 10),
           )
           await asyncio.sleep(2)
       # End
       ls.progress.end(token, types.WorkDoneProgressEnd(message="Finished"))


**After**

::

   from lsprotocol import types
   from pygls.lsp.server import LanguageServer

   server = LanguageServer(name="my-language-server", version="v1.0")

   @server.command('progress.example')
   async def progress(ls: LanguageServer, *args):
       """Create and start the progress on the client."""
       token = str(uuid.uuid4())
       # Create
       await ls.work_done_progress.create_async(token)
       # Begin
       ls.work_done_progress.begin(
           token,
           types.WorkDoneProgressBegin(title="Indexing", percentage=0, cancellable=True),
       )
       # Report
       for i in range(1, 10):
           # Check for cancellation from client
           if ls.work_done_progress.tokens[token].cancelled():
               # ... and stop the computation if client cancelled
               return
           ls.work_done_progress.report(
               token,
               types.WorkDoneProgressReport(message=f"{i * 10}%", percentage=i * 10),
           )
           await asyncio.sleep(2)
       # End
       ls.work_done_progress.end(token, types.WorkDoneProgressEnd(message="Finished"))

Renamed LSP Types
-----------------

As part of the update to ``lsprotocol v2025``, the following types have been renamed.

===================================================================================  ==============
**lsprotocol 2023.x**                                                                **lsprotocol 2025.x**
===================================================================================  ==============
``CancelRequestNotification``                                                        ``CancelNotification``
``ClientRegisterCapabilityRequest``                                                  ``RegistrationRequest``
``ClientRegisterCapabilityResponse``                                                 ``RegistrationResponse``
``ClientUnregisterCapabilityRequest``                                                ``UnregistrationRequest``
``ClientUnregisterCapabilityResponse``                                               ``UnregistrationResponse``
``CodeActionClientCapabilitiesCodeActionLiteralSupportType``                         ``ClientCodeActionLiteralOptions``
``CodeActionClientCapabilitiesCodeActionLiteralSupportTypeCodeActionKindType``       ``ClientCodeActionKindOptions``
``CodeActionClientCapabilitiesResolveSupportType``                                   ``ClientCodeActionResolveOptions``
``CodeActionDisabledType``                                                           ``CodeActionDisabled``
``CompletionClientCapabilitiesCompletionItemKindType``                               ``ClientCompletionItemOptionsKind``
``CompletionClientCapabilitiesCompletionItemType``                                   ``ClientCompletionItemOptions``
``CompletionClientCapabilitiesCompletionItemTypeInsertTextModeSupportType``          ``ClientCompletionItemInsertTextModeOptions``
``CompletionClientCapabilitiesCompletionItemTypeResolveSupportType``                 ``ClientSymbolResolveOptions``
``CompletionClientCapabilitiesCompletionItemTypeTagSupportType``                     ``CompletionItemTagOptions``
``CompletionClientCapabilitiesCompletionListType``                                   ``CompletionListCapabilities``
``CompletionItemResolveRequest``                                                     ``CompletionResolveRequest``
``CompletionItemResolveResponse``                                                    ``CompletionResolveResponse``
``CompletionListItemDefaultsType``                                                   ``CompletionItemDefaults``
``CompletionListItemDefaultsTypeEditRangeType1``                                     ``EditRangeWithInsertReplace``
``CompletionOptionsCompletionItemType``                                              ``ServerCompletionItemOptions``
``CompletionRegistrationOptionsCompletionItemType``                                  ``ServerCompletionItemOptions``
``DocumentSymbolClientCapabilitiesSymbolKindType``                                   ``ClientSymbolKindOptions``
``DocumentSymbolClientCapabilitiesTagSupportType``                                   ``ClientSymbolTagOptions``
``FoldingRangeClientCapabilitiesFoldingRangeKindType``                               ``ClientFoldingRangeKindOptions``
``FoldingRangeClientCapabilitiesFoldingRangeType``                                   ``ClientFoldingRangeOptions``
``GeneralClientCapabilitiesStaleRequestSupportType``                                 ``StaleRequestSupportOptions``
``InitializeParamsClientInfoType``                                                   ``ClientInfo``
``InitializeResultServerInfoType``                                                   ``ServerInfo``
``InlayHintClientCapabilitiesResolveSupportType``                                    ``ClientInlayHintResolveOptions``
``MarkedString_Type1``                                                               ``MarkedStringWithLanguage``
``NotebookDocumentChangeEventCellsType``                                             ``NotebookDocumentCellChanges``
``NotebookDocumentChangeEventCellsTypeStructureType``                                ``NotebookDocumentCellChangeStructure``
``NotebookDocumentChangeEventCellsTypeTextContentType``                              ``NotebookDocumentCellContentChanges``
``NotebookDocumentDidChangeNotification``                                            ``DidChangeNotebookDocumentNotification``
``NotebookDocumentDidCloseNotification``                                             ``DidCloseNotebookDocumentNotification``
``NotebookDocumentDidOpenNotification``                                              ``DidOpenNotebookDocumentNotification``
``NotebookDocumentDidSaveNotification``                                              ``DidSaveNotebookDocumentNotification``
``NotebookDocumentFilter_Type1``                                                     ``NotebookDocumentFilterNotebookType``
``NotebookDocumentFilter_Type2``                                                     ``NotebookDocumentFilterScheme``
``NotebookDocumentFilter_Type3``                                                     ``NotebookDocumentFilterPattern``
``NotebookDocumentSyncOptionsNotebookSelectorType1``                                 ``NotebookDocumentFilterWithNotebook``
``NotebookDocumentSyncOptionsNotebookSelectorType1CellsType``                        ``NotebookCellLanguage``
``NotebookDocumentSyncOptionsNotebookSelectorType2``                                 ``NotebookDocumentFilterWithCells``
``NotebookDocumentSyncOptionsNotebookSelectorType2CellsType``                        ``NotebookCellLanguage``
``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType1``                     ``NotebookDocumentFilterWithNotebook``
``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType1CellsType``            ``NotebookCellLanguage``
``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType2``                     ``NotebookDocumentFilterWithCells``
``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType2CellsType``            ``NotebookCellLanguage``
``PrepareRenameResult_Type1``                                                        ``PrepareRenamePlaceholder``
``PrepareRenameResult_Type2``                                                        ``PrepareRenameDefaultBehavior``
``PublishDiagnosticsClientCapabilitiesTagSupportType``                               ``ClientDiagnosticsTagOptions``
``SemanticTokensClientCapabilitiesRequestsType``                                     ``ClientSemanticTokensRequestOptions``
``SemanticTokensClientCapabilitiesRequestsTypeFullType1``                            ``ClientSemanticTokensRequestFullDelta``
``SemanticTokensOptionsFullType1``                                                   ``SemanticTokensFullDelta``
``SemanticTokensRegistrationOptionsFullType1``                                       ``SemanticTokensFullDelta``
``ServerCapabilitiesWorkspaceType``                                                  ``WorkspaceOptions``
``ShowMessageRequestClientCapabilitiesMessageActionItemType``                        ``ClientShowMessageActionItemOptions``
``SignatureHelpClientCapabilitiesSignatureInformationType``                          ``ClientSignatureInformationOptions``
``SignatureHelpClientCapabilitiesSignatureInformationTypeParameterInformationType``  ``ClientSignatureParameterInformationOptions``
``TextDocumentCodeActionRequest``                                                    ``CodeActionRequest``
``TextDocumentCodeActionResponse``                                                   ``CodeActionResponse``
``TextDocumentCodeLensRequest``                                                      ``CodeLensRequest``
``TextDocumentCodeLensResponse``                                                     ``CodeLensResponse``
``TextDocumentColorPresentationOptions``                                             ``ColorPresentationRequestOptions``
``TextDocumentColorPresentationRequest``                                             ``ColorPresentationRequest``
``TextDocumentColorPresentationResponse``                                            ``ColorPresentationResponse``
``TextDocumentCompletionRequest``                                                    ``CompletionRequest``
``TextDocumentCompletionResponse``                                                   ``CompletionResponse``
``TextDocumentContentChangeEvent_Type1``                                             ``TextDocumentContentChangePartial``
``TextDocumentContentChangeEvent_Type2``                                             ``TextDocumentContentChangeWholeDocument``
``TextDocumentDeclarationRequest``                                                   ``DeclarationRequest``
``TextDocumentDeclarationResponse``                                                  ``DeclarationResponse``
``TextDocumentDefinitionRequest``                                                    ``DefinitionRequest``
``TextDocumentDefinitionResponse``                                                   ``DefinitionResponse``
``TextDocumentDiagnosticRequest``                                                    ``DocumentDiagnosticRequest``
``TextDocumentDiagnosticResponse``                                                   ``DocumentDiagnosticResponse``
``TextDocumentDidChangeNotification``                                                ``DidChangeTextDocumentNotification``
``TextDocumentDidCloseNotification``                                                 ``DidCloseTextDocumentNotification``
``TextDocumentDidOpenNotification``                                                  ``DidOpenTextDocumentNotification``
``TextDocumentDidSaveNotification``                                                  ``DidSaveTextDocumentNotification``
``TextDocumentDocumentColorRequest``                                                 ``DocumentColorRequest``
``TextDocumentDocumentColorResponse``                                                ``DocumentColorResponse``
``TextDocumentDocumentHighlightRequest``                                             ``DocumentHighlightRequest``
``TextDocumentDocumentHighlightResponse``                                            ``DocumentHighlightResponse``
``TextDocumentDocumentLinkRequest``                                                  ``DocumentLinkRequest``
``TextDocumentDocumentLinkResponse``                                                 ``DocumentLinkResponse``
``TextDocumentDocumentSymbolRequest``                                                ``DocumentSymbolRequest``
``TextDocumentDocumentSymbolResponse``                                               ``DocumentSymbolResponse``
``TextDocumentFilter_Type1``                                                         ``TextDocumentFilterLanguage``
``TextDocumentFilter_Type2``                                                         ``TextDocumentFilterScheme``
``TextDocumentFilter_Type3``                                                         ``TextDocumentFilterPattern``
``TextDocumentFoldingRangeRequest``                                                  ``FoldingRangeRequest``
``TextDocumentFoldingRangeResponse``                                                 ``FoldingRangeResponse``
``TextDocumentFormattingRequest``                                                    ``DocumentFormattingRequest``
``TextDocumentFormattingResponse``                                                   ``DocumentFormattingResponse``
``TextDocumentHoverRequest``                                                         ``HoverRequest``
``TextDocumentHoverResponse``                                                        ``HoverResponse``
``TextDocumentImplementationRequest``                                                ``ImplementationRequest``
``TextDocumentImplementationResponse``                                               ``ImplementationResponse``
``TextDocumentInlayHintRequest``                                                     ``InlayHintRequest``
``TextDocumentInlayHintResponse``                                                    ``InlayHintResponse``
``TextDocumentInlineCompletionRequest``                                              ``InlineCompletionRequest``
``TextDocumentInlineCompletionResponse``                                             ``InlineCompletionResponse``
``TextDocumentInlineValueRequest``                                                   ``InlineValueRequest``
``TextDocumentInlineValueResponse``                                                  ``InlineValueResponse``
``TextDocumentLinkedEditingRangeRequest``                                            ``LinkedEditingRangeRequest``
``TextDocumentLinkedEditingRangeResponse``                                           ``LinkedEditingRangeResponse``
``TextDocumentMonikerRequest``                                                       ``MonikerRequest``
``TextDocumentMonikerResponse``                                                      ``MonikerResponse``
``TextDocumentOnTypeFormattingRequest``                                              ``DocumentOnTypeFormattingRequest``
``TextDocumentOnTypeFormattingResponse``                                             ``DocumentOnTypeFormattingResponse``
``TextDocumentPrepareCallHierarchyRequest``                                          ``CallHierarchyPrepareRequest``
``TextDocumentPrepareCallHierarchyResponse``                                         ``CallHierarchyPrepareResponse``
``TextDocumentPrepareRenameRequest``                                                 ``PrepareRenameRequest``
``TextDocumentPrepareRenameResponse``                                                ``PrepareRenameResponse``
``TextDocumentPrepareTypeHierarchyRequest``                                          ``TypeHierarchyPrepareRequest``
``TextDocumentPrepareTypeHierarchyResponse``                                         ``TypeHierarchyPrepareResponse``
``TextDocumentPublishDiagnosticsNotification``                                       ``PublishDiagnosticsNotification``
``TextDocumentRangeFormattingRequest``                                               ``DocumentRangeFormattingRequest``
``TextDocumentRangeFormattingResponse``                                              ``DocumentRangeFormattingResponse``
``TextDocumentRangesFormattingRequest``                                              ``DocumentRangesFormattingRequest``
``TextDocumentRangesFormattingResponse``                                             ``DocumentRangesFormattingResponse``
``TextDocumentReferencesRequest``                                                    ``ReferencesRequest``
``TextDocumentReferencesResponse``                                                   ``ReferencesResponse``
``TextDocumentRenameRequest``                                                        ``RenameRequest``
``TextDocumentRenameResponse``                                                       ``RenameResponse``
``TextDocumentSelectionRangeRequest``                                                ``SelectionRangeRequest``
``TextDocumentSelectionRangeResponse``                                               ``SelectionRangeResponse``
``TextDocumentSemanticTokensFullDeltaRequest``                                       ``SemanticTokensDeltaRequest``
``TextDocumentSemanticTokensFullDeltaResponse``                                      ``SemanticTokensDeltaResponse``
``TextDocumentSemanticTokensFullRequest``                                            ``SemanticTokensRequest``
``TextDocumentSemanticTokensFullResponse``                                           ``SemanticTokensResponse``
``TextDocumentSemanticTokensRangeRequest``                                           ``SemanticTokensRangeRequest``
``TextDocumentSemanticTokensRangeResponse``                                          ``SemanticTokensRangeResponse``
``TextDocumentSignatureHelpRequest``                                                 ``SignatureHelpRequest``
``TextDocumentSignatureHelpResponse``                                                ``SignatureHelpResponse``
``TextDocumentTypeDefinitionRequest``                                                ``TypeDefinitionRequest``
``TextDocumentTypeDefinitionResponse``                                               ``TypeDefinitionResponse``
``TextDocumentWillSaveNotification``                                                 ``WillSaveTextDocumentNotification``
``TextDocumentWillSaveWaitUntilRequest``                                             ``WillSaveTextDocumentWaitUntilRequest``
``TextDocumentWillSaveWaitUntilResponse``                                            ``WillSaveTextDocumentWaitUntilResponse``
``TraceValues``                                                                      ``TraceValue``
``WindowLogMessageNotification``                                                     ``LogMessageNotification``
``WindowShowDocumentRequest``                                                        ``ShowDocumentRequest``
``WindowShowDocumentResponse``                                                       ``ShowDocumentResponse``
``WindowShowMessageNotification``                                                    ``ShowMessageNotification``
``WindowShowMessageRequestRequest``                                                  ``ShowMessageRequest``
``WindowShowMessageRequestResponse``                                                 ``ShowMessageResponse``
``WindowWorkDoneProgressCancelNotification``                                         ``WorkDoneProgressCancelNotification``
``WindowWorkDoneProgressCreateRequest``                                              ``WorkDoneProgressCreateRequest``
``WindowWorkDoneProgressCreateResponse``                                             ``WorkDoneProgressCreateResponse``
``WorkspaceApplyEditRequest``                                                        ``ApplyWorkspaceEditRequest``
``WorkspaceApplyEditResponse``                                                       ``ApplyWorkspaceEditResponse``
``WorkspaceCodeLensRefreshRequest``                                                  ``CodeLensRefreshRequest``
``WorkspaceCodeLensRefreshResponse``                                                 ``CodeLensRefreshResponse``
``WorkspaceConfigurationParams``                                                     ``ConfigurationParams``
``WorkspaceConfigurationRequest``                                                    ``ConfigurationRequest``
``WorkspaceConfigurationResponse``                                                   ``ConfigurationResponse``
``WorkspaceDiagnosticRefreshRequest``                                                ``DiagnosticRefreshRequest``
``WorkspaceDiagnosticRefreshResponse``                                               ``DiagnosticRefreshResponse``
``WorkspaceDidChangeConfigurationNotification``                                      ``DidChangeConfigurationNotification``
``WorkspaceDidChangeWatchedFilesNotification``                                       ``DidChangeWatchedFilesNotification``
``WorkspaceDidChangeWorkspaceFoldersNotification``                                   ``DidChangeWorkspaceFoldersNotification``
``WorkspaceDidCreateFilesNotification``                                              ``DidCreateFilesNotification``
``WorkspaceDidDeleteFilesNotification``                                              ``DidDeleteFilesNotification``
``WorkspaceDidRenameFilesNotification``                                              ``DidRenameFilesNotification``
``WorkspaceEditClientCapabilitiesChangeAnnotationSupportType``                       ``ChangeAnnotationsSupportOptions``
``WorkspaceExecuteCommandRequest``                                                   ``ExecuteCommandRequest``
``WorkspaceExecuteCommandResponse``                                                  ``ExecuteCommandResponse``
``WorkspaceFoldingRangeRefreshRequest``                                              ``FoldingRangeRefreshRequest``
``WorkspaceFoldingRangeRefreshResponse``                                             ``FoldingRangeRefreshResponse``
``WorkspaceInlayHintRefreshRequest``                                                 ``InlayHintRefreshRequest``
``WorkspaceInlayHintRefreshResponse``                                                ``InlayHintRefreshResponse``
``WorkspaceInlineValueRefreshRequest``                                               ``InlineValueRefreshRequest``
``WorkspaceInlineValueRefreshResponse``                                              ``InlineValueRefreshResponse``
``WorkspaceSemanticTokensRefreshRequest``                                            ``SemanticTokensRefreshRequest``
``WorkspaceSemanticTokensRefreshResponse``                                           ``SemanticTokensRefreshResponse``
``WorkspaceSymbolClientCapabilitiesResolveSupportType``                              ``ClientSymbolResolveOptions``
``WorkspaceSymbolClientCapabilitiesSymbolKindType``                                  ``ClientSymbolKindOptions``
``WorkspaceSymbolClientCapabilitiesTagSupportType``                                  ``ClientSymbolTagOptions``
``WorkspaceSymbolLocationType1``                                                     ``LocationUriOnly``
``WorkspaceWillCreateFilesRequest``                                                  ``WillCreateFilesRequest``
``WorkspaceWillCreateFilesResponse``                                                 ``WillCreateFilesResponse``
``WorkspaceWillDeleteFilesRequest``                                                  ``WillDeleteFilesRequest``
``WorkspaceWillDeleteFilesResponse``                                                 ``WillDeleteFilesResponse``
``WorkspaceWillRenameFilesRequest``                                                  ``WillRenameFilesRequest``
``WorkspaceWillRenameFilesResponse``                                                 ``WillRenameFilesResponse``
``WorkspaceWorkspaceFoldersRequest``                                                 ``WorkspaceFoldersRequest``
``WorkspaceWorkspaceFoldersResponse``                                                ``WorkspaceFoldersResponse``
===================================================================================  ==============

Low Level Changes
-----------------

The following changes are unlikely to affect you directly, but have been included for completeness.

``LanguageServer.lsp`` is now ``LanguageServer.protocol``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you need to access the underlying protocol object this is now via the ``protocol`` attribute.

``pygls.server.Server`` is now ``pygls.server.JsonRPCServer``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

pygls' base server class has been renamed

Removed ``loop`` argument from ``pygls.server.JsonRPCServer``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Servers and clients in pygls v2 now both use the high level asyncio API, removing the need for an explicit ``loop`` argument to be passed in.
If you need control over the event loop used by pygls you can use functions like :external:py:func:`asyncio.set_event_loop` before starting the server/client.

Removed ``pygls.protocol.lsp_meta`` module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The implementation of pygls' built-in handlers has changed in v2 and no longer relies on the ``LSPMeta`` metaclass and associated ``call_user_feature`` function.
Therefore both items and the containing module has been removed.

Removed ``multiprocessing.pool.ThreadPool``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :external:py:class:`multiprocessing.pool.ThreadPool` instance has been removed, *pygls* now makes use of :external:py:class:`concurrent.futures.ThreadPoolExecutor` for all threaded tasks.

The ``thread_pool_executor`` attribute of the base ``JsonRPCServer`` class has been removed, the ``ThreadPoolExecutor`` can be accessed via the ``thread_pool`` attribute instead.

``JsonRPCProtocol`` is no longer an ``asyncio.Protocol``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now the pygls v2 uses the high-level asyncio APIs, it no longer makes sense for the ``JsonRPCProtocol`` class to inherit from ``asyncio.Protocol``.
Similarly, "output" classes are now called writers rather than transports. The ``connection_made`` method has been replaced with a corresponding ``set_writer`` method.

New ``pygls.io_`` module
^^^^^^^^^^^^^^^^^^^^^^^^

There is a new ``pygls.io_`` module containing main message parsing loop code common to both client and server

- The equivlaent to pygls v1's ``pygls.server.aio_readline`` function is now ``pygls.io_.run_async``
- It now contains classes like v1's ``WebsocketTransportAdapter``, which have been renamed to ``WebSocketWriter``
