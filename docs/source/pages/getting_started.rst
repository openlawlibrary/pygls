Getting started
===============

This document explains how to install and get started writing Language
servers that are based on *pygls*.

--------------

Installation
------------

To get the latest release from PyPI, simply run:

.. code:: console

   pip install pygls

Alternatively, *pygls* source code can be downloaded from our `GitHub`_
page and installed with following command:

.. code:: console

   python setup.py install

Quick start
-----------

Spin the server up
~~~~~~~~~~~~~~~~~~

*pygls* is a language server framework that can be started without
writing any additional code:

.. code:: python

   from pygls.server import LanguageServer

   server = LanguageServer()

   server.start_tcp('localhost', 8080)

After running the code above, server will start listening for incoming
``Json RPC`` requests on ``http://localhost:8080``.

Register features and commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*pygls* comes with API for registering additional features like
``code completion``, ``find all references``, ``go to definition``, etc…

.. code:: python

   @server.feature(COMPLETION, trigger_characters=[','])
   def completions(params: CompletionParams):
       """Returns completion items."""
       return CompletionList(False, [
           CompletionItem('Item1'),
           CompletionItem('Item2'),
           CompletionItem('Item3'),
       ])

… as well as custom commands:

.. code:: python

   @server.command('myVerySpecialCommandName')
   def cmd_return_hello_world(ls, *args):
       return 'Hello World!'

Features that are currently supported by the LSP specification can be
found in `pygls.features`_ module, while corresponding request/response
classes can be found in `pygls.types`_ module.

Advanced usage
--------------

To reveal the full potential of *pygls* (``thread management``,
``coroutines``, ``multi-root workspace``, ``TCP/IO communication`` etc.)
keep on reading the docs.

Try the example
---------------

We suggest :ref:`setting up the example extension <example-extension>` before
you go further with the documentation, specially if you haven't worked with
language servers before.


.. _GitHub: https://github.com/openlawlibrary/pygls
.. _pygls.features: https://github.com/openlawlibrary/pygls/blob/master/pygls/features.py
.. _pygls.types: https://github.com/openlawlibrary/pygls/blob/master/pygls/types.py
