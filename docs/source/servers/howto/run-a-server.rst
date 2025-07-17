.. _howto-run-server:

How To Run A Server with Python
===============================

This guide explains how to run a language server using a standard CPython interpreter.

Connection Types
----------------

*pygls* in this environment supports :ref:`ls-stdio`, :ref:`ls-tcp` and :ref:`ls-websocket` connections.

.. _ls-stdio:

STDIO
^^^^^

STDIO connections are the default connection type used by most editors and IDEs.
In this mode, the language client is responsible for starting the server as a child process and communicates with it using the stdin and stdout streams.

The :meth:`~pygls.server.JsonRPCServer.start_io` method is used to start the server in *STDIO* mode.

.. code:: python

    from pygls.lsp.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    if __name__ == '__main__':
        server.start_io()

.. _ls-tcp:

TCP
^^^

TCP connections, if supported by the client, allow you to run the server as a separate process independent from the client itself.

In this mode you would first start the language server and then give the server's ``host`` and ``port`` number to the client so that it can establish the connection.

The :meth:`~pygls.server.JsonRPCServer.start_tcp` method is used to start the server in *TCP* mode.


.. code:: python

    from pygls.lsp.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    if __name__ == '__main__':
        server.start_tcp('127.0.0.1', 8080)

.. _ls-websocket:

WEBSOCKETS
^^^^^^^^^^

.. important::

   This connection type requires additional dependencies to be installed.
   Be sure to include the ``ws`` extra when installing *pygls*:

   .. code::

      pip install pygls[ws]

`WEBSOCKET <https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API>`__ connections can be used to expose a language server to a language client running in a web browser.
**Note:** This does NOT mean that the server itself runs in the browser, if you want to run the server itself in the browser, see :ref:`howto-use-pyodide`.

The :meth:`~pygls.server.JsonRPCServer.start_ws` method is used to start the server in *WEBSOCKET* mode.

.. code:: python

    from pygls.lsp.server import LanguageServer

    server = LanguageServer('example-server', 'v0.1')

    if __name__ == '__main__':
        server.start_ws('0.0.0.0', 1234)

CLI Wrapper
-----------

*pygls* provides a simple command line wrapper around these methods allowing the user of your server to select which connection type to use.

.. code:: none

   usage: my-lsp-server [-h] [--tcp] [--ws] [--host HOST] [--port PORT]

   start a LanguageServer instance

   options:
    -h, --help   show this help message and exit
    --tcp        start a TCP server
    --ws         start a WebSocket server
    --host HOST  bind to this address
    --port PORT  bind to this port

Unless given an option like ``--tcp`` or ``--ws``, the wrapper will start the server in *STDIO* mode.

To use it, pass your server instance to the :func:`~pygls.cli.start_server` function.

.. code:: python

   from pygls.cli import run_server
   from pygls.lsp.server import LanguageServer

   server = LanguageServer('example-server', 'v0.1')

   if __name__ == '__main__':
       start_server(server)
