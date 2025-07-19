.. _howto-support-notebooks:

How To Add Notebook Support to a Language Server
=================================================

.. admonition:: Help Wanted!
   :class: tip

   This guide is incomplete and needs to be expanded upon to provide more details to cover topics including:

   - The fallback sync mechanism for notebook documents vs "proper" document synchronization
   - Accessing other details of a notebook document, such as metadata and execution results
   - Reconstructing the JSON representation of a notebook document - `see thie issue comment <https://github.com/openlawlibrary/pygls/issues/394#issuecomment-1749755731>`__

   If this is something you would like to help with, please open an issue or pull request (even if it is a draft!) on our `GitHub <https://github.com/openlawlibrary/pygls>`_, so that we don't accicdentally duplicate your work.

.. seealso::

   :lsp:`notebookDocument/synchronization`
      The section of the LSP specification describing how notebook documents are handled

This guide explains how to add support for notebook documents to your language server.

- A notebook's structure, metadata etc. is represented using the :class:`~lsprotocol.types.NotebookDocument` class from ``lsprotocol``.
- The contents of a single notebook cell is represented using a standard :class:`~pygls.workspace.TextDocument`

In order to receive notebook documents from the client, your language server must provide an instance of :class:`~lsprotocol.types.NotebookDocumentSyncOptions` which declares the kind of notebooks it is interested in

.. code-block:: python

   server = LanguageServer(
       name="example-server",
       version="v0.1",
       notebook_document_sync=types.NotebookDocumentSyncOptions(
           notebook_selector=[
               types.NotebookDocumentFilterWithCells(
                   cells=[
                       types.NotebookCellLanguage(
                           language="python"
                       ),
                   ],
               ),
           ],
       ),
   )

To access the contents of a notebook cell you would call the workspace's :meth:`~pygls.workspace.Workspace.get_text_document` method as normal.

.. code-block:: python

   cell_doc = ls.workspace.get_text_document(cell_uri)

To access the notebook itself call the workspace's :meth:`~pygls.workspace.Workspace.get_notebook_document` method with either the uri of the notebook *or* the uri of any of its cells.

.. code-block:: python

   notebook_doc = ls.workspace.get_notebook_document(notebook_uri=notebook_uri)

   # -- OR --

   notebook_doc = ls.workspace.get_notebook_document(cell_uri=cell_uri)
