
*pygls*
=======

`pygls`_ (pronounced like “pie glass”) is a generic implementation of
the `Language Server Protocol`_ written in the Python programming language. It
allows you to write your own `language server`_ in just a few lines of code::

   from pygls.server import LanguageServer
   from lsprotocol import types

   server = LanguageServer("example-server", "v0.1")

   @server.feature(types.TEXT_DOCUMENT_COMPLETION)
   def completions(params: types.CompletionParams):
       items = []
       document = server.workspace.get_text_document(params.text_document.uri)
       current_line = document.lines[params.position.line].strip()
       if current_line.endswith("hello."):
           items = [
               types.CompletionItem(label="world"),
               types.CompletionItem(label="friend"),
           ]
       return types.CompletionList(is_incomplete=False, items=items)

   if __name__ == "__main__":
       server.start_io()

*pygls* supports

- Python 3.8+ on Windows, MacOS and Linux
- STDIO, TCP/IP and WEBSOCKET communication
- Both sync and async styles of programming
- Running code in background threads
- Automatic text and notebook document syncronisation

.. toctree::
   :hidden:
   :caption: User Guide

   pages/tutorial
   pages/user-guide
   pages/testing

.. toctree::
   :hidden:
   :caption: How To

   Handle Invalid Data <howto/handle-invalid-data>
   Migrate to v1 <howto/migrate-to-v1>

.. toctree::
   :hidden:
   :glob:
   :caption: API Reference

   reference/*

.. toctree::
   :hidden:
   :caption: About

   implementations
   history
   changelog


The documentation is divided up into the following sections

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: User Guide
      :text-align: center

      Step-by-step guides on writing your first language server with *pygls*.

   .. grid-item-card:: How To Guides
      :link: /howto
      :link-type: doc
      :text-align: center

      Short, focused articles on how to acheive a particular outcome

   .. grid-item-card:: API Reference
      :columns: 12
      :text-align: center

      Comprehensive, detailed documentation on all of the features provided by *pygls*.


.. _Language Server Protocol: https://microsoft.github.io/language-server-protocol/specification
.. _Language server: https://langserver.org/
.. _pygls: https://github.com/openlawlibrary/pygls
