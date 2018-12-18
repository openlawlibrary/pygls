.. _tutorial:

Tutorial
========

In order to help you with *pygls* we have created simple, but yet well covered
`Json Extension`_ example.

Prerequisites
-------------

In order to setup and run the example extension, you need following software
installed:

* `Visual Studio Code <https://code.visualstudio.com/>`_  editor
* `Python 3.5+ <https://www.python.org/downloads/>`_
* Cloned `pygls <https://github.com/openlawlibrary/pygls>`_ repository

.. note::
    If you have created virtual environment, make sure that you have
    *pygls* installed and `selected appropriate python interpreter <https://code.visualstudio.com/docs/python/environments>`_
    for the *pygls* project.


Running the Example
-------------------

For a step-by-step guide on how to run the example follow `README`_.

Hacking the Extension
---------------------

When you have successfully setup and run the extension, open `server.py`_ and
go through the code.

We have implemented following capabilities:

- ``textDocument/completion`` feature
- ``countDownBlocking`` command
- ``countDownNonBlocking`` command
- ``showConfiguration`` command
- ``textDocument/didChange`` feature
- ``textDocument/didClose`` feature
- ``textDocument/didOpen`` feature

When running the extension in *debug* mode, you can set breakpoints to see
when each of above mentioned actions gets triggered.

Blocking Command Test
~~~~~~~~~~~~~~~~~~~~~

1. Press **F1**, find and run ``Count down 10 seconds [Blocking]`` command.
2. Try to show *code completions* while counter is still ticking.

Language server is **blocked** and the reason is ``time.sleep`` which is a
**blocking** operation.

.. hint::
    To make this command **non blocking**, add ``@json_server.thread()``
    decorator, like in code below:

    .. code-block:: python

        @json_server.thread()
        @json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
        def count_down_10_seconds_blocking(ls, *args):
            # Omitted

    *pygls* uses **thread pool** to execute functions that are marked with
    ``thread`` decorator.


Non-Blocking Command Test
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Press **F1**, find and run ``Count down 10 seconds [Non Blocking]`` command.
2. Try to show *code completions* while counter is still ticking.

The language server is **not blocked** because we used ``asyncio.sleep`` this
time, while it's still executing *just* in the *main* thread.


.. _Json Extension: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension
.. _README: https://github.com/openlawlibrary/pygls/blob/master/examples/README.md
.. _server.py: https://github.com/openlawlibrary/pygls/blob/master/examples/json-extension/server/server.py
