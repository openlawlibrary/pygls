.. pygls documentation master file, created by
   sphinx-quickstart on Sun Nov 25 16:16:27 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pygls
=====

*pygls* (pronounced like “spy glass”) is generic implementation of
`Language Server Protocol`_ written in Python programming language. It
allows you to write your own `Language Server`_ in just few lines of
code.

Features
--------

-  cross-platform support
-  TCP/IP and IO communication
-  runs in asyncio event loop
-  register LSP features and custom commands as:

   -  asynchronous functions (coroutines)
   -  synchronous functions
   -  functions that will be executed in separate thread

-  thread management
-  in-memory workspace with incremental document updates
-  good test coverage

Python versions
---------------

*pygls* works with Python 3.5+.

User Guide
----------

.. toctree::
   :maxdepth: 2

   pages/getting_started
   pages/tutorial
   pages/advanced_usage
   pages/testing


.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/specification
.. _Language Server: https://langserver.org/
