.. _tutorial:

Tutorial
========

In order to help you with *pygls*, we have created a simple
`json-extension`_ example.

Prerequisites
-------------

In order to setup and run the example extension, you need following software
installed:

* `Visual Studio Code <https://code.visualstudio.com/>`_ editor
* `Python 3.7+ <https://www.python.org/downloads/>`_
* `vscode-python <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_ extension
* A clone of the `pygls <https://github.com/openlawlibrary/pygls>`_ repository

.. note::
    If you have created virtual environment, make sure that you have *pygls* installed
    and `selected appropriate python interpreter <https://code.visualstudio.com/docs/python/environments>`_
    for the *pygls* project.


Running the Example
-------------------

For a step-by-step guide on how to setup and run the example follow `README`_.

Hacking the Extension
---------------------

When you have successfully setup and run the extension, open `server.py`_ and
go through the code.

We have implemented following capabilities:

- ``textDocument/completion`` feature
- ``countDownBlocking`` command
- ``countDownNonBlocking`` command
- ``textDocument/didChange`` feature
- ``textDocument/didClose`` feature
- ``textDocument/didOpen`` feature
- ``showConfigurationAsync`` command
- ``showConfigurationCallback`` command
- ``showConfigurationThread`` command

When running the extension in *debug* mode, you can set breakpoints to see
when each of above mentioned actions gets triggered.

Visual Studio Code supports *Language Server Protocol*, which means, that every
action on the client-side, will result in sending request or notification to
the server via JSON RPC.

Debug Code Completions
~~~~~~~~~~~~~~~~~~~~~~

Set a breakpoint inside ``completion`` function and go back to opened *json*
file in your editor. Now press ``ctrl + space`` (``control + space`` on mac) to
show completion list and you will hit the breakpoint. When you continue
debugging, the completion list pop-up won't show up because it was closing when
the editor lost focus.

Similarly, you can debug any feature or command.

Keep the breakpoint and continue to the next section.

Blocking Command Test
~~~~~~~~~~~~~~~~~~~~~

In order to demonstrate you that blocking the language server will reject other
requests, we have registered a custom command which counts down 10 seconds and
sends notification messages to the client.

1. Press **F1**, find and run ``Count down 10 seconds [Blocking]`` command.
2. Try to show *code completions* while counter is still ticking.

Language server is **blocked**, because ``time.sleep`` is a
**blocking** operation. This is why you didn't hit the breakpoint this time.

.. hint::
    To make this command **non blocking**, add ``@json_server.thread()``
    decorator, like in code below:

    .. code-block:: python

        @json_server.thread()
        @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
        def count_down_10_seconds_blocking(ls, *args):
            # Omitted

    *pygls* uses a **thread pool** to execute functions that are marked with
    a ``thread`` decorator.


Non-Blocking Command Test
~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3.4 introduced *asyncio* module which allows us to use asynchronous
functions (aka *coroutines*) and do `cooperative multitasking`_. Using the
`await` keyword inside your coroutine will give back control to the
scheduler and won't block the main thread.

1. Press **F1** and run the ``Count down 10 seconds [Non Blocking]`` command.
2. Try to show *code completions* while counter is still ticking.

Bingo! We hit the breakpoint! What just happened?

The language server was **not blocked** because we used ``asyncio.sleep`` this
time. The language server was executing *just* in the *main* thread.


Text Document Operations
~~~~~~~~~~~~~~~~~~~~~~~~

Opening and closing a JSON file will display appropriate notification message
in the bottom right corner of the window and the file content will be
validated. Validation will be performed on content changes, as well.

Show Configuration Data
~~~~~~~~~~~~~~~~~~~~~~~

There are *three* ways for getting configuration section from the client
settings.

.. note::

    *pygls*' built-in coroutines are suffixed with *async* word, which means that
    you have to use the *await* keyword in order to get the result (instead of
    *asyncio.Future* object).

- **Get the configuration inside a coroutine**

.. code-block:: python

    config = await ls.get_configuration_async(ConfigurationParams([
        ConfigurationItem('', JsonLanguageServer.CONFIGURATION_SECTION)
    ]))

- **Get the configuration inside a normal function**

We already saw that we *don't* want to block the main thread. Sending the
configuration request to the client will result with the response from it, but
we don't know when. You have to pass *callback* function which will be
triggered once response from the client is received.

.. code-block:: python

    def _config_callback(config):
        try:
            example_config = config[0].exampleConfiguration

            ls.show_message(
                f'jsonServer.exampleConfiguration value: {example_config}'
            )

        except Exception as e:
            ls.show_message_log(f'Error ocurred: {e}')

    ls.get_configuration(ConfigurationParams([
        ConfigurationItem('', JsonLanguageServer.CONFIGURATION_SECTION)
    ]), _config_callback)

As you can see, the above code is hard to read.

- **Get the configuration inside a threaded function**

Blocking operations such as ``future.result(1)`` should not be used inside
normal functions, but to increase the code readability, you can add the
*thread* decorator to your function to use *pygls*' *thread pool*.

.. code-block:: python

    @json_server.thread()
    @json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
    def show_configuration_thread(ls: JsonLanguageServer, *args):
        """Gets exampleConfiguration from the client settings using a thread pool."""
        try:
            config = ls.get_configuration(ConfigurationParams([
                ConfigurationItem('', JsonLanguageServer.CONFIGURATION_SECTION)
            ])).result(2)

            # ...

This way you won't block the main thread. *pygls* will start a new thread when
executing the function.

Modify the Example
~~~~~~~~~~~~~~~~~~

We encourage you to continue to :ref:`advanced section <advanced-usage>` and
modify this example.

.. _json-extension: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension
.. _README: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension/README.md
.. _server.py: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension/server/server.py
.. _cooperative multitasking: https://en.wikipedia.org/wiki/Cooperative_multitasking
