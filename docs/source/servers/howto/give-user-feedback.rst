.. _howto-give-user-feedback:

How To Give User Feedback
=========================


.. admonition:: Help Wanted!
   :class: tip

   This guide is incomplete and needs to be expanded upon to provide more details to cover topics including:

   - Work done progress
   - Show document
   - Show message (request)

   If this is something you would like to help with, please open an issue or pull request (even if it is a draft!) on our `GitHub <https://github.com/openlawlibrary/pygls>`_, so that we don't accicdentally duplicate your work.


The LSP protocol provides a number of ways to give feedback to the user.

Show Message (Notification)
---------------------------

:lsp:`window/showMessage` is a notification that is sent from the server to the client to display a prominant text message. e.g. VSCode will render this as a notification popup

.. code:: python

   @server.command('countdown.async')
   async def count_down_10_seconds_non_blocking(ls, *args):
       for i in range(10):
           # Sends message notification to the client
           ls.show_message(f"Counting down... {10 - i}")
           await asyncio.sleep(1)

Show Message Log
----------------

:lsp:`window/logMessage` is a notification that is sent from the server to the client to display a discrete text message. e.g. VSCode will display the message in an :guilabel:`Output` channel.

.. code:: python

   @server.command('countdown.async')
   async def count_down_10_seconds_non_blocking(ls, *args):
       for i in range(10):
           # Sends message log notification to the client
           ls.show_message_log(f"Counting down... {10 - i}")
           await asyncio.sleep(1)
