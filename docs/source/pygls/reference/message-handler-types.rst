.. _message-handlers:

Message Handler Types
=====================

*pygls* supports executing many types of message handler functions.

- :ref:`message-handler-async`
- :ref:`message-handler-sync`
- :ref:`message-handler-thread`

.. _message-handler-async:

*Asynchronous* Functions (*Coroutines*)
---------------------------------------

The code snippet below shows how to register a command as a coroutine:

.. code:: python

    @server.command('countdown.async')
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

.. _message-handler-sync:

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

    @server.command('countdown.blocking')
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted

Registering *feature* as a regular function is exactly the same.

.. warning::

    Using computation intensive operations will *block* the main thread and
    should be *avoided* inside regular functions. Take a look at
    `threaded functions <#threaded-functions>`__ for more details.

.. _message-handler-thread:

*Threaded* Functions
^^^^^^^^^^^^^^^^^^^^

*Threaded* functions are just regular functions, but marked with
*pygls*'s ``thread`` decorator:

.. code:: python

    # Decorator order is not important in this case
    @server.thread()
    @server.command('countdown.threaded')
    def count_down_10_seconds_blocking(ls, *args):
        # Omitted

*pygls* uses its own *thread pool* to execute above function in *daemon*
thread and it is *lazy* initialized first time when function marked with
``thread`` decorator is fired.

*Threaded* functions can be used to run blocking operations. If it has been a
while or you are new to threading in Python, check out Python's
``multithreading`` and `GIL <https://en.wikipedia.org/wiki/Global_interpreter_lock>`__
before messing with threads.
