*pygls*
=======

`pygls`_ (pronounced like “pie glass”) is a generic implementation of
the `Language Server Protocol`_ written in the Python programming language. It
allows you to write your own `language server`_ in just a few lines of code

.. literalinclude:: ../../examples/hello-world/main.py
   :language: python

*pygls* supports

- Python 3.8+ on Windows, MacOS and Linux
- STDIO, TCP/IP and WEBSOCKET communication
- Both sync and async styles of programming
- Running code in background threads
- Automatic text and notebook document syncronisation

.. toctree::
   :hidden:
   :caption: User Guide

   getting-started
   user-guide
   How To <howto>
   reference

.. toctree::
   :hidden:
   :caption: About

   implementations
   history
   changelog


The documentation is divided up into the following sections

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: Getting Started
      :link: /getting-started
      :link-type: doc
      :text-align: center

      First steps with *pygls*.

   .. grid-item-card:: How To Guides
      :link: /howto
      :link-type: doc
      :text-align: center

      Short, focused articles on how to acheive a particular outcome

   .. grid-item-card:: API Reference
      :link: /reference
      :link-type: doc
      :columns: 12
      :text-align: center

      Comprehensive, detailed documentation on all of the features provided by *pygls*.


.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/specification
.. _Language server: https://langserver.org/
.. _pygls: https://github.com/openlawlibrary/pygls
