.. _howto-work-with-text-documents:

How To Work with Text Documents
===============================


.. admonition:: Help Wanted!
   :class: tip

   This guide is incomplete and needs to be expanded upon to provide more details to cover topics including:

   - (Breif!) explanation of the position encoding handshake during ``initialize``
   - Using the ``PositionCodec`` to convert between LSP and Python positions (and why it's necessary)

   If this is something you would like to help with, please open an issue or pull request (even if it is a draft!) on our `GitHub <https://github.com/openlawlibrary/pygls>`_, so that we don't accicdentally duplicate your work.


This guide explains how to access :class:`TextDocuments <pygls.workspace.TextDocument>` via the :class:`~pygls.workspace.Workspace` in your language server.

Accessing Text Documents
------------------------

The state of all :class:`TextDocuments <pygls.workspace.TextDocument>` in the user's project are managed by the :class:`~pygls.workspace.Workspace` object attached to every language server.

Text documents are identified by their uri which is typically included with the ``params`` object for the current message.
Passing the uri to the :meth:`~pygls.workspace.Workspace.get_text_document` method will return the corresponding document.

.. code:: python

   @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
   async def did_open(ls, params: types.DidOpenTextDocumentParams):

       # Get document from workspace
       text_doc = ls.workspace.get_text_document(params.text_document.uri)


Accessing Document Contents
---------------------------

Once you have a :class:`TextDocument <pygls.workspace.TextDocument>` you can access its contents via the :attr:`~pygls.workspace.TextDocument.source` attribute.

.. code:: python

   @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
   async def did_open(ls, params: types.DidOpenTextDocumentParams):

       text_doc = ls.workspace.get_text_document(params.text_document.uri)
       contents = text_doc.source
       ...

It's common to want to process the individual lines of a text document, in which case you can use the :attr:`~pygls.workspace.TextDocument.lines` property to access all of the lines

.. code:: python

   @server.feature(types.TEXT_DOCUMENT_DID_OPEN)
   async def did_open(ls, params: types.DidOpenTextDocumentParams):

       text_doc = ls.workspace.get_text_document(params.text_document.uri)
       for line in text_doc.lines:
           ...

Editing Text Documents
----------------------

There are scenarios where you may want to edit the contents of a text document, for example when implementing a quickfix or refactoring command.

This is done by instructing the client to apply an edit on your behalf using the :lsp:`workspace/applyEdit` request.
The following example is taken from our example :doc:`/servers/examples/code-lens` server

.. literalinclude:: ../../../../examples/servers/code_lens.py
   :language: python
   :start-at: @server.command
   :end-before: if __name__
