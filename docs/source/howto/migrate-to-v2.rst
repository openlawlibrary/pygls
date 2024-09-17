How To Migrate to v2.0
======================


.. note::

   This guide is still a draft, some details may change

The highlight of the *pygls* v2 release is upgrading ``lsprotocol`` to ``v2024.x`` bringing with it support for the proposed LSP v3.18 types and methods.
The new version includes standardised object names (so no more classes like ``NotebookDocumentSyncRegistrationOptionsNotebookSelectorType2CellsType``!)

With the major version bump, this release also takes the opportunity to clean up the codebase by removing deprecated code and renaming a few things to try and improve overall consistency.
This guide outlines how to adapt an existing server to the breaking changes introduced in this release.

**Known Migrations**

You may find these projects that have already successfully migrated to v2 a useful reference:

- Our `example servers <https://github.com/openlawlibrary/pygls/commit/e90f88ad642a20d3a16551e00a5a0abe0a1e041f>`__
- `pytest-lsp <https://github.com/swyddfa/lsp-devtools/pull/177>`__
- `esbonio <https://github.com/swyddfa/esbonio/pull/882>`__

Python Support
--------------

*pygls v2* removes support for Python 3.8 and adds support for Python 3.13 (with the GIL, you are welcome to try the free-threaded version just note that it has not been tested yet!)


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
``Worspace.get_document``                           ``Workspace.get_text_document``
``Worspace.put_document``                           ``Workspace.put_text_document``
``Worspace.remove_document``                        ``Workspace.remove_text_document``
``Worspace.update_document``                        ``Workspace.update_text_document``
==================================================  ==============

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

As part of the update to ``lsprotocol v2024``, the following types have been renamed.

===================================================================================  ==============
**lsprotocol 2023.x**                                                                **lsprotocol 2024.x**
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

Removed ``multiprocessing.pool.ThreadPool``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :external:py:class:`multiprocessing.pool.ThreadPool` instance has been removed, *pygls* now makes use of :external:py:class:`concurrent.futures.ThreadPoolExecutor` for all threaded tasks.

The ``thread_pool_executor`` attribute of the base ``JsonRPCServer`` class has been removed, the ``ThreadPoolExecutor`` can be accessed via the ``thread_pool`` attribute instead.
