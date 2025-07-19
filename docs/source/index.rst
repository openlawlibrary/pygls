*pygls*
=======

`pygls`_ (pronounced like “pie glass”) is a generic implementation of
the `Language Server Protocol`_ written in the Python programming language. It
allows you to write your own `language server`_ in just a few lines of code

.. literalinclude:: ../../examples/hello-world/main.py
   :language: python

*pygls* supports

- Python 3.9+ on Windows, MacOS and Linux
- **Experimental** support for Pyodide
- STDIO, TCP/IP and WEBSOCKET communication
- Both sync and async styles of programming
- Running code in background threads
- Automatic text and notebook document syncronisation

.. toctree::
   :hidden:
   :caption: Language Servers

   servers/getting-started
   How To <servers/howto>
   servers/reference

.. toctree::
   :hidden:
   :caption: Language Clients

   clients/index

.. toctree::
   :hidden:
   :caption: The Protocol

   protocol/howto

.. toctree::
   :hidden:
   :caption: The Library

   pygls/howto
   pygls/reference
   pygls/api-reference

.. toctree::
   :hidden:
   :caption: Contributing

   contributing/howto

.. toctree::
   :hidden:
   :caption: About

   implementations
   history
   changelog

Navigation
----------

*The pygls documentation tries to (with varying degrees of success!) follow the* `Diátaxis <https://diataxis.fr/>`__ *approach to writing documentation*

This documentation site is divided up into the following sections

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: Language Servers
      :link: servers/getting-started
      :link-type: doc
      :text-align: center

      Documentation specific to implementing Language Servers using *pygls*.

   .. grid-item-card:: Language Clients
      :text-align: center

      Documentation specific to implementing Language Clients using *pygls*.
      Coming Soon\ :sup:`TM`!

   .. grid-item-card:: The Protocol
      :link: protocol/howto
      :link-type: doc
      :text-align: center

      Additional articles that explain some aspect of the Language Server Protocol in general.

   .. grid-item-card:: The Library
      :link: pygls/howto
      :link-type: doc
      :text-align: center

      Documentation that applies to the *pygls* library itself e.g. migration guides.

   .. grid-item-card:: Contributing
      :link: contributing/howto
      :link-type: doc
      :text-align: center

      Guides on how to contribute to *pygls*.

   .. grid-item-card:: About
      :text-align: center

      Additional context on the *pygls* project.

.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/specification
.. _Language server: https://langserver.org/
.. _pygls: https://github.com/openlawlibrary/pygls
