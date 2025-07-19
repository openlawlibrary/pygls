.. _user-guide:

User Guide
==========

Language Server
---------------

The language server is responsible for managing the connection with the client as well as sending and receiving messages over
the `Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__
which is based on the `Json RPC protocol <https://www.jsonrpc.org/specification>`__.



Overriding ``LanguageServerProtocol``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a reason to override the existing ``LanguageServerProtocol`` class,
you can do that by inheriting the class and passing it to the ``LanguageServer``
constructor.


.. _passing-instance:

Passing Language Server Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using language server methods inside registered features and commands are quite
common. We recommend adding language server as a **first parameter** of a
registered function.

There are two ways of doing this:

- **ls** (**l**\anguage **s**\erver) naming convention

Add **ls** as first parameter of a function and *pygls* will automatically pass
the language server instance.

.. code-block:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted


- add **type** to first parameter

Add the **LanguageServer** class or any class derived from it as a type to
first parameter of a function

.. code-block:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
    def count_down_10_seconds_blocking(ser: JsonLanguageServer, *args):
        # Omitted


Using outer ``json_server`` instance inside registered function will make
writing unit :ref:`tests <testing>` more difficult.

Communicating with the Client
-----------------------------

.. important::

   Most of the messages listed here cannot be sent until the LSP session has been initialized.
   See the section on the :lsp:`initiaiize` request in the specification for more details.

In addition to responding to requests, there are a number of additional messages a server can send to the client.


Publish Diagnostics
~~~~~~~~~~~~~~~~~~~

:lsp:`textDocument/publishDiagnostics` notifications are sent from the server to the client to highlight errors or potential issues. e.g. syntax errors or unused variables.

Usually this notification is sent after document is opened, or on document content change:

.. code:: python

   @json_server.feature(TEXT_DOCUMENT_DID_OPEN)
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

Show Message
~~~~~~~~~~~~

:lsp:`window/showMessage` is a notification that is sent from the server to the client to display a prominant text message. e.g. VSCode will render this as a notification popup

.. code:: python

   @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
   async def count_down_10_seconds_non_blocking(ls, *args):
       for i in range(10):
           # Sends message notification to the client
           ls.show_message(f"Counting down... {10 - i}")
           await asyncio.sleep(1)

Show Message Log
~~~~~~~~~~~~~~~~

:lsp:`window/logMessage` is a notification that is sent from the server to the client to display a discrete text message. e.g. VSCode will display the message in an :guilabel:`Output` channel.

.. code:: python

   @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
   async def count_down_10_seconds_non_blocking(ls, *args):
       for i in range(10):
           # Sends message log notification to the client
           ls.show_message_log(f"Counting down... {10 - i}")
           await asyncio.sleep(1)


Custom Notifications
~~~~~~~~~~~~~~~~~~~~

.. warning::

   Custom notifications are not part of the LSP specification and dedicated support for your custom notification(s) will have to be added to each language client you intend to support.

A custom notification can be sent to the client using the :meth:`~pygls.server.LanguageServer.send_notification` method

.. code:: python

   server.send_notification('myCustomNotification', 'test data')
