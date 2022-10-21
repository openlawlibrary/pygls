Getting Started
===============

This document explains how to install *pygls* and get started writing language
servers that are based on it.

.. note::

    Before going any further, if you are not familiar with *language servers*
    and *Language Server Protocol*, we recommend reading following articles:

        - `Language Server Protocol Overview <https://microsoft.github.io/language-server-protocol/overview>`_
        - `Language Server Protocol Specification <https://microsoft.github.io/language-server-protocol/specification>`_
        - `Language Server Protocol SDKs <https://microsoft.github.io/language-server-protocol/implementors/sdks/>`_


Installation
------------

To get the latest release from *PyPI*, simply run:

.. code:: console

   pip install pygls

Alternatively, *pygls* source code can be downloaded from our `GitHub`_
page and installed with following command:

.. code:: console

   python setup.py install

Quick Start
-----------

Spin the Server Up
~~~~~~~~~~~~~~~~~~

*pygls* is a language server that can be started without writing any additional
code:

.. code:: python

   from pygls.server import LanguageServer

   server = LanguageServer('example-server', 'v0.1')

   server.start_tcp('127.0.0.1', 8080)

After running the code above, server will start listening for incoming
``Json RPC`` requests on ``http://127.0.0.1:8080``.

Register Features and Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*pygls* comes with an API for registering additional features like
``code completion``, ``find all references``, ``go to definition``, etc.

.. code:: python

    @server.feature(COMPLETION, CompletionOptions(trigger_characters=[',']))
    def completions(params: CompletionParams):
        """Returns completion items."""
        return CompletionList(
            is_incomplete=False,
            item=[
                CompletionItem(label='Item1'),
                CompletionItem(label='Item2'),
                CompletionItem(label='Item3'),
            ]
        )

… as well as custom commands:

.. code:: python

   @server.command('myVerySpecialCommandName')
   def cmd_return_hello_world(ls, *args):
       return 'Hello World!'

Features that are currently supported by the LSP specification can be
found in `pygls.lsp.methods`_ module, while corresponding request/response
classes can be found in `pygls.lsp.types`_ module.

Advanced usage
--------------

To reveal the full potential of *pygls* (``thread management``, ``coroutines``,
``multi-root workspace``, ``TCP/STDIO communication``, etc.) keep reading.

Tutorial
--------

We recommend completing the :ref:`tutorial <tutorial>`, especially if you
haven't worked with language servers before.


.. _GitHub: https://github.com/openlawlibrary/pygls
.. _pygls.lsp.methods: https://github.com/openlawlibrary/pygls/blob/master/pygls/lsp/methods.py
.. _pygls.lsp.types: https://github.com/openlawlibrary/pygls/tree/master/pygls/lsp/types
