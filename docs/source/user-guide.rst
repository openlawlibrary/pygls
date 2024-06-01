.. _user-guide:

User Guide
==========

Language Server
---------------

The language server is responsible for managing the connection with the client as well as sending and receiving messages over
the `Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__
which is based on the `Json RPC protocol <https://www.jsonrpc.org/specification>`__.

Connections
~~~~~~~~~~~

*pygls* supports :ref:`ls-tcp`, :ref:`ls-stdio` and :ref:`ls-websocket` connections.

.. _ls-tcp:

TCP
^^^

TCP connections are usually used while developing the language server.
This way the server can be started in *debug* mode separately and wait
for the client connection.

.. note:: Server should be started **before** the client.

The code snippet below shows how to start the server in *TCP* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    server.start_tcp('127.0.0.1', 8080)

.. _ls-stdio:

STDIO
^^^^^

STDIO connections are useful when client is starting the server as a child
process. This is the way to go in production.

The code snippet below shows how to start the server in *STDIO* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    server.start_io()

.. _ls-websocket:

WEBSOCKET
^^^^^^^^^

WEBSOCKET connections are used when you want to expose language server to
browser based editors.

The code snippet below shows how to start the server in *WEBSOCKET* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    server.start_ws('0.0.0.0', 1234)

Logging
~~~~~~~

Logs are useful for tracing client requests, finding out errors and
measuring time needed to return results to the client.

*pygls* uses built-in python *logging* module which has to be configured
before server is started.

Official documentation about logging in python can be found
`here <https://docs.python.org/3/howto/logging-cookbook.html>`__. Below
is the minimal setup to setup logging in *pygls*:

.. code:: python

    import logging

    from pygls.server import LanguageServer

    logging.basicConfig(filename='pygls.log', filemode='w', level=logging.DEBUG)

    server = LanguageServer('example-server', 'v0.1')

    server.start_io()

Overriding ``LanguageServerProtocol``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a reason to override the existing ``LanguageServerProtocol`` class,
you can do that by inheriting the class and passing it to the ``LanguageServer``
constructor.

Custom Error Reporting
~~~~~~~~~~~~~~~~~~~~~~

The default :class:`~pygls.server.LanguageServer` will send a :lsp:`window/showMessage` notification to the client to display any uncaught exceptions in the server.
To override this behaviour define your own :meth:`~pygls.server.LanguageServer.report_server_error` method like so:

.. code:: python

   class CustomLanguageServer(LanguageServer):
       def report_server_error(self, error: Exception, source: Union[PyglsError, JsonRpcException]):
           pass

Handling Client Messages
------------------------

.. admonition:: Requests vs Notifications

   Unlike a *request*, a *notification* message has no ``id`` field and the server *must not* reply to it.
   This means that, even if you return a result inside a handler function for a notification, the result won't be passed to the client.

   The ``Language Server Protocol``, unlike ``Json RPC``, allows bidirectional communication between the server and the client.

For the majority of the time, a language server will be responding to requests and notifications sent from the client.
*pygls* refers to the handlers for all of these messages as *features* with one exception.

The Language Server protocol allows a server to define named methods that a client can invoke by sending a :lsp:`workspace/executeCommand` request.
Unsurprisingly, *pygls* refers to these named methods a *commands*.

*Built-In* Features
~~~~~~~~~~~~~~~~~~~

*pygls* comes with following predefined set of handlers for the following
`Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__
(LSP) features:

.. note::

    *Built-in* features in most cases should *not* be overridden.

    If you need to do some additional processing of one of the messages listed below, register a feature with the same name and your handler will be called immediately after the corresponding built-in feature.

**Lifecycle Messages**

- The :lsp:`initialize` request is sent as a first request from client to the server to setup their communication.
  *pygls* automatically computes registered LSP capabilities and sends them as part of the :class:`~lsprotocol.types.InitializeResult` response.

- The :lsp:`shutdown` request is sent from the client to the server to ask the server to shutdown.

- The :lsp:`exit` notification is sent from client to the server to ask the server to exit the process.
  *pygls* automatically releases all resources and stops the process.

**Text Document Synchronization**

- The :lsp:`textDocument/didOpen` notification will tell *pygls* to create a document in the in-memory workspace which will exist as long as the document is opened in editor.

- The :lsp:`textDocument/didChange` notification will tell *pygls* to update the document text.
  *pygls* supports *full* and *incremental* document changes.

- The :lsp:`textDocument/didClose` notification will tell *pygls* to remove a document from the in-memory workspace.

**Notebook Document Synchronization**

- The :lsp:`notebookDocument/didOpen` notification will tell *pygls* to create a notebook document in the in-memory workspace which will exist as long as the document is opened in editor.

- The :lsp:`notebookDocument/didChange` notification will tell *pygls* to update the notebook document include its content, metadata, execution results and cell structure.

- The :lsp:`notebookDocument/didClose` notification will tell *pygls* to remove the notebook from the in-memory workspace.

**Miscellanous**

- The :lsp:`workspace/didChangeWorkspaceFolders` notification will tell *pygls* to update in-memory workspace folders.

- The :lsp:`workspace/executeCommand` request will tell *pygls* to execute a custom command.

- The :lsp:`$/setTrace` notification tells *pygls* to update the server's :class:`TraceValue <lsprotocol.types.TraceValues>`.

.. _ls-handlers:

Registering Handlers
~~~~~~~~~~~~~~~~~~~~

.. seealso::

   It's recommended that you follow the :ref:`tutorial <tutorial>` before reading this section.

- The :func:`~pygls.server.LanguageServer.feature` decorator is used to register a handler for a given LSP message.
- The :func:`~pygls.server.LanguageServer.command` decorator is used to register a named command.

The following applies to both feature and command handlers.

Language servers using *pygls* run in an *asyncio event loop*.
They *asynchronously* listen for incoming messages and, depending on the way handler is registered, apply different execution strategies to process the message.

Depending on the use case, handlers can be registered in three different ways:

- as an :ref:`async <ls-handler-async>` function
- as a :ref:`synchronous <ls-handler-sync>` function
- as a :ref:`threaded <ls-handler-thread>` function

.. _ls-handler-async:

*Asynchronous* Functions (*Coroutines*)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*pygls* supports ``python 3.8+`` which has a keyword ``async`` to
specify coroutines.

The code snippet below shows how to register a command as a coroutine:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
    async def count_down_10_seconds_non_blocking(ls, *args):
        # Omitted

Registering a *feature* as a coroutine is exactly the same.

Coroutines are functions that are executed as tasks in *pygls*'s *event
loop*. They should contain at least one *await* expression (see
`awaitables <https://docs.python.org/3.5/glossary.html#term-awaitable>`__
for details) which tells event loop to switch to another task while
waiting. This allows *pygls* to listen for client requests in a
*non blocking* way, while still only running in the *main* thread.

Tasks can be canceled by the client if they didn't start executing (see
`Cancellation
Support <https://microsoft.github.io/language-server-protocol/specification#cancelRequest>`__).

.. warning::

    Using computation intensive operations will *block* the main thread and
    should be *avoided* inside coroutines. Take a look at
    `threaded functions <#threaded-functions>`__ for more details.

.. _ls-handler-sync:

*Synchronous* Functions
^^^^^^^^^^^^^^^^^^^^^^^

Synchronous functions are regular functions which *blocks* the *main*
thread until they are executed.

`Built-in features <#built-in-features>`__ are registered as regular
functions to ensure correct state of language server initialization and
workspace.

The code snippet below shows how to register a command as a regular
function:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted

Registering *feature* as a regular function is exactly the same.

.. warning::

    Using computation intensive operations will *block* the main thread and
    should be *avoided* inside regular functions. Take a look at
    `threaded functions <#threaded-functions>`__ for more details.

.. _ls-handler-thread:

*Threaded* Functions
^^^^^^^^^^^^^^^^^^^^

*Threaded* functions are just regular functions, but marked with
*pygls*'s ``thread`` decorator:

.. code:: python

    # Decorator order is not important in this case
    @json_server.thread()
    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted

*pygls* uses its own *thread pool* to execute above function in *daemon*
thread and it is *lazy* initialized first time when function marked with
``thread`` decorator is fired.

*Threaded* functions can be used to run blocking operations. If it has been a
while or you are new to threading in Python, check out Python's
``multithreading`` and `GIL <https://en.wikipedia.org/wiki/Global_interpreter_lock>`__
before messing with threads.

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

Configuration
~~~~~~~~~~~~~

The :lsp:`workspace/configuration` request is sent from the server to the client in order to fetch configuration settings from the client.
Depending on how the handler is registered (see :ref:`here <ls-handlers>`) you can use the :meth:`~pygls.server.LanguageServer.get_configuration` or :meth:`~pygls.server.LanguageServer.get_configuration_async` methods to request configuration from the client:

-  *asynchronous* functions (*coroutines*)

   .. code:: python

      # await keyword tells event loop to switch to another task until notification is received
      config = await ls.get_configuration(
          WorkspaceConfigurationParams(
              items=[
                  ConfigurationItem(scope_uri='doc_uri_here', section='section')
              ]
          )
      )

-  *synchronous* functions

   .. code:: python

      # callback is called when notification is received
      def callback(config):
          # Omitted

      params = WorkspaceConfigurationParams(
          items=[
              ConfigurationItem(scope_uri='doc_uri_here', section='section')
          ]
      )
      config = ls.get_configuration(params, callback)

-  *threaded* functions

   .. code:: python

      # .result() will block the thread
      config = ls.get_configuration(
          WorkspaceConfigurationParams(
              items=[
                  ConfigurationItem(scope_uri='doc_uri_here', section='section')
              ]
          )
      ).result()

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

Workspace Edits
~~~~~~~~~~~~~~~

The :lsp:`workspace/applyEdit` request allows your language server to ask the client to modify particular documents in the client's workspace.

.. code:: python

   def apply_edit(self, edit: WorkspaceEdit, label: str = None) -> ApplyWorkspaceEditResponse:
       # Omitted

   def apply_edit_async(self, edit: WorkspaceEdit, label: str = None) -> ApplyWorkspaceEditResponse:
       # Omitted

Custom Notifications
~~~~~~~~~~~~~~~~~~~~

.. warning::

   Custom notifications are not part of the LSP specification and dedicated support for your custom notification(s) will have to be added to each language client you intend to support.

A custom notification can be sent to the client using the :meth:`~pygls.server.LanguageServer.send_notification` method

.. code:: python

   server.send_notification('myCustomNotification', 'test data')


The Workspace
-------------

The :class:`~pygls.workspace.Workspace` is a python object that holds information about workspace folders, opened documents and is responsible for synchronising server side document state with that of the client.

**Text Documents**

The :class:`~pygls.workspace.TextDocument` class is how *pygls* represents a text document.
Given a text document's uri the :meth:`~pygls.workspace.Workspace.get_text_document` method can be used to access the document itself:

.. code:: python

   @json_server.feature(TEXT_DOCUMENT_DID_OPEN)
   async def did_open(ls, params: DidOpenTextDocumentParams):

       # Get document from workspace
       text_doc = ls.workspace.get_text_document(params.text_document.uri)

**Notebook Documents**

.. seealso::

   See the section on :lsp:`notebookDocument/synchronization` in the specification for full details on how notebook documents are handled

- A notebook's structure, metadata etc. is represented using the :class:`~lsprotocol.types.NotebookDocument` class from ``lsprotocol``.
- The contents of a single notebook cell is represented using a standard :class:`~pygls.workspace.TextDocument`

In order to receive notebook documents from the client, your language server must provide an instance of :class:`~lsprotocol.types.NotebookDocumentSyncOptions` which declares the kind of notebooks it is interested in

.. code-block:: python

   server = LanguageServer(
       name="example-server",
       version="v0.1",
       notebook_document_sync=types.NotebookDocumentSyncOptions(
           notebook_selector=[
               types.NotebookDocumentSyncOptionsNotebookSelectorType2(
                   cells=[
                       types.NotebookDocumentSyncOptionsNotebookSelectorType2CellsType(
                           language="python"
                       )
                   ]
               )
           ]
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
