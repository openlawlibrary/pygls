Built-In Features
=================

The base :class:`~pygls.lsp.server.LanguageServer` class comes out of the box with many low-level LSP features already implemented.
This page lists all of these features and the behaviour that *pygls* implements.

.. note::

   It is **NOT** possible to override or disable these features, but you can shadow (most of) them by registering your own handlers using the standard :deco:`server.feature <pygls.server.JsonRPCServer.feature>` decorator.

   *pygls* will arrange to call your handler at an appropriate time, see the description of the individual features below for details on exactly when your handler will be called.

Lifecycle Messages
------------------

*pygls* automatically handles the messages that control the overall lifecycle of an LSP session

``initialize``
^^^^^^^^^^^^^^

The :lsp:`initialize` request is the first message sent in a LSP session.

As part of the request, the client provides details about the user's project (e.g. which folders are in the workspace) as well as details about the client itself (e.g. which features of the LSP specification it supports).

In response, the server provides which features it supports so the client knows what information it can expect the server to provide.
Along with initializing the :class:`~pygls.workspace.Workspace`, *pygls* automatically computes your server's capabilities based on the features you have registered.

.. admonition:: Custom Handler

   If you provide your own ``initialize`` handler, it will be called **after** the server has initialized the workspace,
   but **before** computing your server's capabilities.
   This means you can register additional features based on the client's capabilities or provided initialization options.

   .. literalinclude:: ../../../../examples/servers/register_during_initialize.py
      :language: python
      :start-at: @server.feature
      :end-at: return None

``shutdown``
^^^^^^^^^^^^

The :lsp:`shutdown` request is sent from the client to the server to ask the server to shutdown.
If you have any resources that need to be cleaned up at the end of a session, doing so within a ``shutdown`` handler is the ideal place.

.. admonition:: Custom Handler

   If you provide your own ``shutdown`` handler, it will be called **before** the built-in handler.

``exit``
^^^^^^^^

The :lsp:`exit` notification is sent from client to the server to ask the server to exit the process. *pygls* automatically stops the process by calling :external+python:py:func:`sys.exit`

.. admonition:: Custom Handler

   If you provide your own ``exit`` handler, it will be called **before** the built-in handler.


Text Document Synchronization
-----------------------------

*pygls* automatically handles the messages used to ensure that both the language client and server agree on the contents of plain text documents in the user's workspace.

.. note::

   In addition to the features listed below, `specification <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_synchronization>`__ defines messages like :lsp:`textDocument/didSave` and :lsp:`textDocument/willSave`.

   *pygls* does not currently provide any default behaviour for these.

``textDocument/didOpen``
^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`textDocument/didOpen` notification informs *pygls* that the client has taken ownership of the contents of the given text document and that the copy of the document on disk should not be trusted.

.. admonition:: Custom Handler

   If you provide your own ``textDocument/didOpen`` handler, it will be called **after** the built-in handler.

``testDocument/didChange``
^^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`textDocument/didChange` notification informs *pygls* of changes made to the document's contents.

.. admonition:: Custom Handler

   If you provide your own ``textDocument/didChange`` handler, it will be called **after** the built-in handler.
   Therefore, your handler will see the document with the changes provided by the client already applied.

``textDocument/didClose``
^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`textDocument/didClose` notification informs *pygls* that the client has released ownership of the document and that the copy of the document on disk can be trusted again.

.. admonition:: Custom Handler

   If you provide your own ``textDocument/didClose`` handler, it will be called **after** the built-in handler.

Notebook Document Synchronization
---------------------------------

*pygls* automatically handles the messages used to ensure that both the language client and server agree on the contents and structure of notebook documents in the user's workspace.

.. tip::

   See :ref:`howto-support-notebooks` for details on adding notebook document support to your language server.

``notebookDocument/didOpen``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`notebookDocument/didOpen` notification informs *pygls* that the client has taken ownership of the contents of the given notebook document and that the copy of the document on disk should not be trusted.

.. admonition:: Custom Handler

   If you provide your own ``notebookDocument/didOpen`` handler, it will be called **after** the built-in handler.

``notebookDocument/didChange``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`notebookDocument/didChange` notification informs *pygls* of changes made to the document's content, metadata, execution results and cell structure.

.. admonition:: Custom Handler

   If you provide your own ``notebookDocument/didChange`` handler, it will be called **after** the built-in handler.
   Therefore, your handler will see the document with the changes provided by the client already applied.

``notebookDocument/didClose``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`notebookDocument/didClose` notification informs *pygls* that the client has released ownership of the document and that the copy of the document on disk can be trusted again.

.. admonition:: Custom Handler

   If you provide your own ``notebookDocument/didClose`` handler, it will be called **after** the built-in handler.

Miscellanous
------------

*pygls* also handles the following messages

``workspace/didChangeWorkspaceFolders``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :lsp:`workspace/didChangeWorkspaceFolders` notification informs *pygls* when the user adds or removes folders from the workspace.

.. admonition:: Custom Handler

   If you provide your own ``workspace/didChangeWorkspaceFolders`` handler, it will be called **after** the built-in handler.

``workspace/executeCommand``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. tip::

   See :ref:`howto-implement-commands` for details on how to implement custom commands in your language server.

The :lsp:`workspace/executeCommand` request is sent when the client wants to invoke a custom command provided by the server.

.. admonition:: Custom Handler
   :class: warning

   It is **not** possible to provide a custom handler for this request.

``$/cancelRequest``
^^^^^^^^^^^^^^^^^^^

The :lsp:`$/cancelRequest` notification informs *pygls* that the client is no longer interested in the result of a request it previously sent and if possible it should stop processing it.

.. admonition:: Custom Handler
   :class: warning

   It is **not** possible to provide a custom handler for this request.

``$/setTrace``
^^^^^^^^^^^^^^

The :lsp:`$/setTrace` notification tells *pygls* to update the server's :class:`TraceValue <lsprotocol.types.TraceValues>`.

.. admonition:: Custom Handler

   If you provide your own ``$/setTrace`` handler, it will be called **after** the built-in handler.
