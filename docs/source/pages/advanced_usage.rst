.. _advanced-usage:

Advanced Usage
==============

Language Server
---------------

The language server is responsible for receiving and sending messages over
the `Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__
which is based on the `Json RPC protocol <https://www.jsonrpc.org/specification>`__.

Connections
~~~~~~~~~~~

*pygls* supports *TCP* and socket *STDIO* connections.

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

STDIO
^^^^^

STDIO connections are useful when client is starting the server as a child
process. This is the way to go in production.

The code snippet below shows how to start the server in *STDIO* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    server.start_io()

WEBSOCKET
^^^^^^^^^

WEBSOCKET connections are used when you want to expose language server to
browser based editors.

The code snippet below shows how to start the server in *WEBSOCKET* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    server.start_websocket('0.0.0.0', 1234)

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

Features
--------

What is a feature in *pygls*? In terms of language servers and the
`Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__,
a feature is one of the predefined methods from
LSP `specification <https://microsoft.github.io/language-server-protocol/specification>`__,
such as: *code completion*, *formatting*, *code lens*, etc. Features
that are available can be found in `pygls.lsp.methods`_ module.

*Built-In* Features
~~~~~~~~~~~~~~~~~~~

*pygls* comes with following predefined set of
`Language Server Protocol <https://microsoft.github.io/language-server-protocol/>`__
(LSP) features:

-  The `initialize <https://microsoft.github.io/language-server-protocol/specification#initialize>`__
   request is sent as a first request from client to the server to setup
   their communication. *pygls* automatically computes registered LSP
   capabilities and sends them as part of ``InitializeResult`` response.

-  The `shutdown <https://microsoft.github.io/language-server-protocol/specification#shutdown>`__
   request is sent from the client to the server to ask the server to
   shutdown.

-  The `exit <https://microsoft.github.io/language-server-protocol/specification#exit>`__
   notification is sent from client to the server to ask the server to
   exit the process. *pygls* automatically releases all resources and
   stops the process.

-  The `textDocument/didOpen <https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen>`__
   notification will tell *pygls* to create a document in the in-memory
   workspace which will exist as long as document is opened in editor.

-  The `textDocument/didChange <https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange>`__
   notification will tell *pygls* to update the document text.
   *pygls* supports _full_ and _incremental_ document changes.

-  The `textDocument/didClose <https://microsoft.github.io/language-server-protocol/specification#textDocument_didClose>`__
   notification will tell *pygls* to remove a document from the
   in-memory workspace.

-  The `workspace/didChangeWorkspaceFolders <https://microsoft.github.io/language-server-protocol/specification#workspace_didChangeWorkspaceFolders>`__
   notification will tell *pygls* to update in-memory workspace folders.

Commands
--------

Commands can be treated as a *custom features*, i.e. everything that is
not covered by LSP specification, but needs to be implemented.

API
---

*Feature* and *Command* Advanced Registration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*pygls* is a language server which relies on *asyncio event loop*. It is
*asynchronously* listening for incoming messages and, depending on the
way method is registered, applying different execution strategies to
respond to the client.

Depending on the use case, *features* and *commands* can be registered
in three different ways.

To make sure that you fully understand what is happening under the hood,
please take a look at the :ref:`tutorial <tutorial>`.

.. note::

    *Built-in* features in most cases should *not* be overridden.
    Instead, register the feature with the same name and it will be
    called immediately after the corresponding built-in feature.

*Asynchronous* Functions (*Coroutines*)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*pygls* supports ``python 3.7+`` which has a keyword ``async`` to
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


Notifications
~~~~~~~~~~~~~

A *notification* is a request message without the ``id`` field and server
*must not* reply to it. This means that, if your language server received the
notification, even if you return the result inside your handler function,
the result won't be passed to the client.

The ``Language Server Protocol``, unlike ``Json RPC``, allows bidirectional
communication between the server and the client.

Configuration
^^^^^^^^^^^^^

The `configuration <https://microsoft.github.io/language-server-protocol/specification#workspace_configuration>`__
request is sent from the server to the client in order to fetch
configuration settings from the client. When the requested configuration
is collected, the client sends data as a notification to the server.

.. note::

    Although ``configuration`` is a ``request``, it is explained in this
    section because the client sends back the ``notification`` object.

The code snippet below shows how to send configuration to the client:

.. code:: python

    def get_configuration(self,
                          params: ConfigurationParams,
                          callback: Optional[Callable[[List[Any]], None]] = None
                          ) -> asyncio.Future:
        # Omitted

*pygls* has three ways for handling configuration notification from the
client, depending on way how the function is registered (described
`here <#feature-and-command-advanced-registration>`__):

-  *asynchronous* functions (*coroutines*)

.. code:: python

    # await keyword tells event loop to switch to another task until notification is received
    config = await ls.get_configuration(ConfigurationParams(items=[ConfigurationItem(scope_uri='doc_uri_here', section='section')]))

-  *synchronous* functions

.. code:: python

    # callback is called when notification is received
    def callback(config):
        # Omitted

    config = ls.get_configuration(ConfigurationParams(items=[ConfigurationItem(scope_uri='doc_uri_here', section='section')]), callback)

-  *threaded* functions

.. code:: python

    # .result() will block the thread
    config = ls.get_configuration(ConfigurationParams(items=[ConfigurationItem(scope_uri='doc_uri_here', section='section')])).result()

Show Message
^^^^^^^^^^^^

`Show
message <https://microsoft.github.io/language-server-protocol/specification#window_showMessage>`__
is notification that is sent from the server to the client to display
text message.

The code snippet below shows how to send show message notification:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
    async def count_down_10_seconds_non_blocking(ls, *args):
        for i in range(10):
            # Sends message notification to the client
            ls.show_message(f"Counting down... {10 - i}")
            await asyncio.sleep(1)

Show Message Log
^^^^^^^^^^^^^^^^

`Show message
log <https://microsoft.github.io/language-server-protocol/specification#window_logMessage>`__
is notification that is sent from the server to the client to display
text message in the output channel.

The code snippet below shows how to send show message log notification:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
    async def count_down_10_seconds_non_blocking(ls, *args):
        for i in range(10):
            # Sends message log notification to the client's output channel
            ls.show_message_log(f"Counting down... {10 - i}")
            await asyncio.sleep(1)

Publish Diagnostics
^^^^^^^^^^^^^^^^^^^

`Publish
diagnostics <https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics>`__
notifications are sent from the server to the client to signal results
of validation runs.

Usually this notification is sent after document is opened, or on
document content change, e.g.:

.. code:: python

    @json_server.feature(TEXT_DOCUMENT_DID_OPEN)
    async def did_open(ls, params: DidOpenTextDocumentParams):
        """Text document did open notification."""
        ls.show_message("Text Document Did Open")
        ls.show_message_log("Validating json...")

        # Get document from workspace
        text_doc = ls.workspace.get_document(params.text_document.uri)

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


Custom Notifications
^^^^^^^^^^^^^^^^^^^^

*pygls* supports sending custom notifications to the client and below
is method declaration for this functionality:

.. code:: python

    def send_notification(self, method: str, params: object = None) -> None:
        # Omitted

And method invocation example:

.. code:: python

    server.send_notification('myCustomNotification', 'test data')

Custom Error Reporting
^^^^^^^^^^^^^^^^^^^^^^

By default Pygls notifies the client to display any occurences of uncaught exceptions in the
server. To override this behaviour define your own `report_server_error()` method like so:

.. code:: python

    Class CustomLanguageServer(LanguageServer):
        def report_server_error(self, error: Exception, source: Union[PyglsError, JsonRpcException]):
            pass


Workspace
~~~~~~~~~

`Workspace <https://github.com/openlawlibrary/pygls/blob/master/pygls/workspace.py>`__
is a python object that holds information about workspace folders, opened
documents and has the logic for updating document content.

*pygls* automatically take care about mentioned features of the
workspace.

Workspace methods that can be used for user defined features are:

-  Get document from the workspace

.. code:: python

        def get_document(self, doc_uri: str) -> Document:
            # Omitted

-  `Apply
   edit <https://microsoft.github.io/language-server-protocol/specification#workspace_applyEdit>`__
   request

.. code:: python

    def apply_edit(self, edit: WorkspaceEdit, label: str = None) -> ApplyWorkspaceEditResponse:
        # Omitted


.. _pygls.lsp.methods: https://github.com/openlawlibrary/pygls/blob/master/pygls/lsp/methods.py
.. _pygls.lsp.types: https://github.com/openlawlibrary/pygls/tree/master/pygls/lsp/types
