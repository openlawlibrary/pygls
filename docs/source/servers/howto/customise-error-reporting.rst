.. _howto-customise-error-reporting:

How To Customise Error Reporting
================================

The default :class:`~pygls.lsp.server.LanguageServer` will send a :lsp:`window/showMessage` notification to the client to display any uncaught exceptions in the server.
To override this behaviour define your own :meth:`~pygls.lsp.server.LanguageServer.report_server_error` method like so:

.. code:: python

   from pygls.exceptions import PyglsError, JsonRpcException
   from pygls.lsp.server import LanguageServer

   class CustomLanguageServer(LanguageServer):
       def report_server_error(self, error: Exception, source: PyglsError | JsonRpcException):
           pass
