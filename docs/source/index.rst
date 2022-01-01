.. pygls documentation master file, created by
   sphinx-quickstart on Sun Nov 25 16:16:27 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

*pygls*
=======

`pygls`_ (pronounced like “pie glass”) is a generic implementation of
the `Language Server Protocol`_ written in the Python programming language. It
allows you to write your own `language server`_ in just a few lines of code.

Features
--------

-  cross-platform support
-  TCP/IP and STDIO communication
-  runs in asyncio event loop
-  register LSP features and custom commands as:

   -  asynchronous functions (coroutines)
   -  synchronous functions
   -  functions that will be executed in separate thread

-  thread management
-  in-memory workspace with _full_ and _incremental_ document updates
-  type-checking
-  good test coverage

Python Versions
---------------

*pygls* works with Python 3.7+.

User Guide
----------

.. toctree::
   :maxdepth: 2

   pages/getting_started
   pages/tutorial
   pages/advanced_usage
   pages/testing


.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/specification
.. _Language server: https://langserver.org/
.. _pygls: https://github.com/openlawlibrary/pygls
