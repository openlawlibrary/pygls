.. _howto-access-server-instance:

How To Access the Server Instance
=================================

Using language server methods inside registered features and commands are quite common.
We recommend adding language server as a **first parameter** of a registered function.

.. admonition:: Why not use ``server`` inside the function?
   :class: tip

   Using the outer ``server`` instance inside registered function will make writing unit :ref:`tests <testing>` more difficult as you can no longer simulate different scenarios by modifying the server instance you pass to the handler function.


There are two ways of doing this:

- Add a **type annotation** to first parameter (recommended)

  Add the **LanguageServer** class (or any class derived from it) as the type annotation to first parameter of a function, pygls will detect this and automatically pass the language server instance.

  .. code-block:: python

      @server.command('countdown.blocking')
      def count_down_10_seconds_blocking(ser: JsonLanguageServer, *args):
          # Omitted


- **ls** (**l**\anguage **s**\erver) naming convention (preserved for backwards compatibility)

  Name the first parameter **ls**, *pygls* will automatically pass the language server instance.

  .. code-block:: python

      @server.command('countdown.blocking')
      def count_down_10_seconds_blocking(ls, *args):
          # Omitted
