.. _howto-implement-diagnostics:

How To Implement Diagnostics
============================

.. admonition:: Help Wanted!
   :class: tip

   This guide is incomplete and needs to be expanded upon to provide more details to cover topics including:

   - Discussion of pull vs push diagnostics

   If this is something you would like to help with, please open an issue or pull request (even if it is a draft!) on our `GitHub <https://github.com/openlawlibrary/pygls>`_, so that we don't accicdentally duplicate your work.

Publish (Push Model) Diagnostics
--------------------------------

:lsp:`textDocument/publishDiagnostics` notifications are sent from the server to the client to highlight errors or potential issues. e.g. syntax errors or unused variables.

Usually this notification is sent after document is opened, or on document content change:

.. code:: python

   @server.feature(TEXT_DOCUMENT_DID_OPEN)
   async def did_open(ls, params: DidOpenTextDocumentParams):
       """Text document did open notification."""
       ls.show_message("Text Document Did Open")
       ls.show_message_log("Validating json...")

       # Get document from workspace
       text_doc = ls.workspace.get_text_document(params.text_document.uri)

       diagnostic = Diagnostic(
          range=Range(
              start=Position(line-1, col-1),
              end=Position(line-1, col)
          ),
          message="Custom validation message",
          source="Json Server"
       )

       # Send diagnostics
       ls.publish_diagnostics(text_doc.uri, [diagnostic])
