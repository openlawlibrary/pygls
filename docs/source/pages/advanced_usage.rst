.. _advanced-usage:

Advanced Usage
==============

Language Server
---------------

The language server is responsible for receiving and sending messages over
the ``Language Server Protocol`` which is based on `Json RPC
protocol <https://www.jsonrpc.org/specification>`__.

Connections
~~~~~~~~~~~

*pygls* supports **TCP** and socket **STDIO** types of connections.

TCP
^^^

TCP connections are usually used while developing the language server.
This way server can be started in *debug* mode separately and wait for
client connection.

.. note:: Server should be started **before** the client.

The code snippet below shows how to start the server in *TCP* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer()

    server.start_tcp('localhost', 8080)

STDIO
^^^^^

STDIO connections are useful when client is starting the server as a child
process and usually this is the way to go in production.

The code snippet below shows how to start the server in *STDIO* mode.

.. code:: python

    from pygls.server import LanguageServer

    server = LanguageServer()

    server.start_io()

Logging
~~~~~~~

Logs are useful for tracing client requests, finding out errors and
measuring time needed to return results to the client.

*pygls* uses built-in python *logging* module which has to be configured
before server is started.

Official documentation about logging in python can be found
`here <https://docs.python.org/3/howto/logging-cookbook.html>`__, and
below is the minimal setup to setup logging in *pygls*:

.. code:: python

    import logging

    from pygls.server import LanguageServer

    logging.basicConfig(filename='pygls.log', filemode='w', level=logging.DEBUG)

    server = LanguageServer()

    server.start_io()

Features
--------

What is a feature in *pygls*? In terms of language servers and the
``Language Server Protocol``, a feature is one of the predefined methods from
LSP `specification <https://microsoft.github.io/language-server-protocol/specification>`__,
such as: *code completion*, *formatting*, *code lens*, etc. Features
that are available can be found in `pygls.features <../features>`__
module.

*Built-In* Features
~~~~~~~~~~~~~~~~~~~

*pygls* comes with following predefined set of
``Language Server Protocol`` (LSP) features:

-  `initialize <https://microsoft.github.io/language-server-protocol/specification#initialize>`__
   request is sent as a first request from client to the server to setup
   their communication. *pygls* automatically computes registered LSP
   capabilities and sends them as part of ``InitializeResult`` response.

-  `shutdown <https://microsoft.github.io/language-server-protocol/specification#shutdown>`__
   request is sent from the client to the server to ask the server to
   shutdown.

-  `exit <https://microsoft.github.io/language-server-protocol/specification#exit>`__
   notification is sent from client to the server to ask the server to
   exit the process. *pygls* automatically releases all resources and
   stops the process.

-  `textDocument/didOpen <https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen>`__
   notification will tell *pygls* to create a document in the in-memory
   workspace which will exist as long as document is opened in editor.

-  `textDocument/didChange <https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange>`__
   notification will tell *pygls* to update the document text. For now,
   *pygls* supports **only** incremental document changes.

-  `textDocument/didClose <https://microsoft.github.io/language-server-protocol/specification#textDocument_didClose>`__
   notification will tell *pygls* to remove a document from the
   in-memory workspace.

-  `workspace/didChangeWorkspaceFolders <https://microsoft.github.io/language-server-protocol/specification#workspace_didChangeWorkspaceFolders>`__
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
please take a look at the example
`server <../examples/json-extension/server/server.py>`__ and test it
following these `instructions <../examples/README.md>`__.

.. note:: *Built-in* features in most cases should *not* overridden. Instead, register feature with the same name and it will be called immediately after the corresponding built-in feature.

*Asynchronous* Functions (*Coroutines*)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*pygls* supports ``python 3.5+`` which has a keyword ``async`` to
specify coroutines.

The code snippet below shows how to register a command as a coroutine:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
    async def count_down_10_seconds_non_blocking(ls, *args):
        # Omitted

Registering a *feature* as a coroutine is exactly the same.

Coroutines are functions that are executed as tasks in *pygls*'s *event
loop*. They should contain at least one *await* expression (more about
`awaitables <https://docs.python.org/3.5/glossary.html#term-awaitable>`__)
which tells event loop to switch to another task while waiting. This
allows *pygls* to listen for client requests in a *non blocking* way,
while still only running in the *main* thread.

Tasks can be canceled by the client if they didn't start executing (see
`Cancellation
Support <https://microsoft.github.io/language-server-protocol/specification#cancelRequest>`__).

.. warning:: Using computation intensive operations will *block* the main thread and should be *avoided* inside coroutines. Take a look at `threaded functions <#threaded-functions>`__ for more details.

*Synchronous* Functions
^^^^^^^^^^^^^^^^^^^^^^^

Synchronous functions are regular functions which *blocks* the *main*
thread until they are executed.

`Built-in features <#Built-in-features>`__ are registered as regular
functions to ensure correct state of language server initialization and
workspace.

The code snippet below shows how to register a command as a regular
function:

.. code:: python

    @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted

Registering *feature* as a regular function is exactly the same.

.. warning:: Using computation intensive operations will *block* the main thread and should be *avoided* inside regular functions. Take a look at `threaded functions <#threaded-functions>`__ for more details.

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

Notification is a request message without ``id`` field and server *must
not* reply to it. This means that, if your language server received the
notification, even if you return result inside your handler function,
the result won't be passed to the client.

The ``Language Server Protocol``, unlike ``Json RPC``, allows bidirectional
communication between the server and the client.

Configuration
^^^^^^^^^^^^^

The `configuration <https://microsoft.github.io/language-server-protocol/specification#workspace_configuration>`__
request is sent from the server to the client in order to fetch
configuration settings from the client. When the requested configuration
is collected, the client sends data as a notification to the server.

.. note:: Although ``configuration`` is a ``request``, it is explained in this section because the client sends back the ``notification`` object.

The code snippet below shows how to send configuration to the client:

.. code:: python

    def get_configuration(self,
                          params: ConfigurationParams,
                          callback: Optional[Callable[[List[Any]], None]] = None
                          ) -> asyncio.Future:
        # Omitted

*pygls* has three ways for handling configuration notification from the
client, depending on way how the function is registered (described
`here <#Feature-and-command-advanced-registration>`__):

-  *asynchronous* functions (*coroutines*)

.. code:: python

    # await keyword tells event loop to switch to another task until notification is received
    config = await ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')]))

-  *synchronous* functions

.. code:: python

    # callback is called when notification is received
    def callback(config):
        # Omitted

    config = ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')]), callback)

-  *threaded* functions

.. code:: python

    # .result() will block the thread
    config = ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')])).result()

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
            ls.workspace.show_message("Counting down... {}".format(10 - i))
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
            ls.workspace.show_message_log("Counting down... {}".format(10 - i))
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
        ls.workspace.show_message("Text Document Did Open")
        ls.workspace.show_message_log("Validating json...")

        # Get document from workspace
        text_doc = ls.workspace.get_document(params.textDocument.uri)

        diagnostic = Diagnostic(
                         range=Range(Position(line-1, col-1), Position(line-1, col)),
                         message="Custom validation message",
                         source="Json Server"
                     )

        # Send diagnostics
        ls.workspace.publish_diagnostics(text_doc.uri, [diagnostic])

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

Workspace
~~~~~~~~~

`Workspace <../pygls/workspace.py>`__ is a python object that holds
information about workspace folders, opened documents and has the logic
for updating document content.

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

