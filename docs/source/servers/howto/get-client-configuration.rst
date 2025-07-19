.. howto-get-client-configuration:

How To Get Client Configuration
===============================

.. admonition:: Help Wanted!
   :class: tip

   This guide is incomplete and needs to be expanded upon to provide more details to cover topics including:

   - Elaborate more on sections and configuration scopes.

   If this is something you would like to help with, please open an issue or pull request (even if it is a draft!) on our `GitHub <https://github.com/openlawlibrary/pygls>`_, so that we don't accicdentally duplicate your work.

The LSP specification allows servers to request configuration options from the client.
This is done using the :lsp:`workspace/configuration` request.

You can use the :meth:`~pygls.lsp.server.LanguageServer.workspace_configuration` or :meth:`~pygls.lsp.server.LanguageServer.workspace_configuration_async` methods to request configuration from the client:

-  *asynchronous* functions (*coroutines*)

   .. code:: python

      # await keyword tells event loop to switch to another task until notification is received
      config = await ls.workspace_configuration_async(
          types.ConfigurationParams(
              items=[
                  types.ConfigurationItem(scope_uri='doc_uri_here', section='section')
              ]
          )
      )

-  *synchronous* functions

   .. code:: python

      # callback is called when notification is received
      def callback(config):
          # Omitted

      params = types.ConfigurationParams(
          items=[
              types.ConfigurationItem(scope_uri='doc_uri_here', section='section')
          ]
      )
      config = ls.workspace_configuration(params, callback)

-  *threaded* functions

   .. code:: python

      # .result() will block the thread
      config = ls.workspace_configuration(
          types.ConfigurationParams(
              items=[
                  types.ConfigurationItem(scope_uri='doc_uri_here', section='section')
              ]
          )
      ).result()
