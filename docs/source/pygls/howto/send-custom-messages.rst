.. _howto-send-custom-messages:

How To Send Custom Messages
===========================


.. admonition:: Work in Progress
   :class: note

   This guide needs more detail

A custom notification can be sent to the client (or server) using the :meth:`~pygls.protocol.JsonRPCProtocol.notify` method of the underlying protocol object

.. code-block:: python

   server.protocol.notify('my/customNotification', {"example": "data"})

Simiarly, the :meth:`~pygls.protocol.JsonRPCProtocol.send_request` and :meth:`~pygls.protocol.JsonRPCProtocol.send_request_async` methods can be used to send a custom request

.. code-block:: python

   response = client.protocol.send_request('my/customRequest', {"example": "data"})

   response = await client.protocol.send_request_async('my/customRequest', {"example": "data"})

Depending on your use case this may be sufficient however, you lose all typing information this way.
It is possible to extend the :class:`~pygls.protocol.LanguageServerProtocol` object used by *pygls* (or in fact define a completely custom :class:`~pygls.protocol.JsonRPCProtocol`!)

Extending ``LanguageServerProtocol``
------------------------------------

.. code-block:: python

   from pygls.protocol import LanguageServerProtocol


   class MyCustomExtension(LanguageServerProtocol):

      def __init__(self, server: LanguageServer, converter: Converter):
         super().__init__(server, converter)

      def get_message_type(self, method: str) -> Type[Any] | None:
         """Return my custom message types, falling back to ``LanguageServerProtocol``
         where needed"""

         if method == "my/customRequest":
             return MyCustomRequest

         return super().get_message_type(method)

      def get_result_type(self, method: str) -> Type[Any] | None:
         """Return my custom response types, falling back to ``LanguageServerProtocol``
         where needed"""

         if method == "my/customRequest":
             return MyCustomResponse

         return super().get_result_type(method)

To use your custom protocol type, pass it to the :class:`~pygls.lsp.server.LanguageServer`

.. code-block::

   server = LanguageServer(
       name="my-language-server",
       version="v1.0",
       protocol_cls=MyCustomExtension,
   )

Defining a Custom Protocol
--------------------------

A similar approach is needed to define an entirely custom JSON-RPC protocol

.. code-block:: python

   from pygls.protocol import JsonRPCProtocol, default_converter
   from pygls.server import JsonRPCServer

   class MyCustomProtocol(JsonRPCProtocol):

      def __init__(self, server: LanguageServer, converter: Converter):
         super().__init__(server, converter)

      def get_message_type(self, method: str) -> Type[Any] | None:
          ...

      def get_result_type(self, method: str) -> Type[Any] | None:
          ...

   server = JsonRPCServer(
       protocol_cls=MyCustomProtocol,
       converter_factory=default_converter,
   )
