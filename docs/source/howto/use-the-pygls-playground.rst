.. _howto-use-pygls-playground:

How To Use the ``pygls-playground`` Extension
=============================================

.. figure:: https://user-images.githubusercontent.com/2675694/260591942-b7001a7b-3081-439d-b702-5f8a489856db.png
   :target: https://user-images.githubusercontent.com/2675694/260591942-b7001a7b-3081-439d-b702-5f8a489856db.png
   :align: center

   Screenshot of the pygls-playground extension in action

The ``pygls-playground`` VSCode extension has two main goals.

- Provide an environment in which you can easily experiment with the pygls framework by trying some of our example servers - or by writing your own

- Provide a minimal example of what it takes to integrate a pygls powered language server into VSCode.

.. tip::

   For a more complete example of a VSCode client, check out Microsoft's `template extension for Python tools <https://github.com/microsoft/vscode-python-tools-extension-template>`__.

Setup
-----

.. highlight:: none

Since the ``pygls-playground`` is not a general purpose extension it is distributed as a `local workspace <https://code.visualstudio.com/updates/v1_89#_local-workspace-extensions>`__ extension.
This does mean, you will have to build the extension yourself before you can use it.

.. _howto-use-pygls-playground-install-pygls:

Install *pygls*
^^^^^^^^^^^^^^^

#. If you have not done so already, clone the `pygls <https://github.com/openlawlibrary/pygls>`__ GitHub repository::

   $ git clone https://github.com/openlawlibrary/pygls

#. Open a terminal in the repository's root directory and create a virtual environment::

   $ python3 -m venv env

#. Activate the environment::

   $ source ./env/bin/activate


#. Install `pygls`::

   (env) $ python -m pip install -e .


Compile the Extension
^^^^^^^^^^^^^^^^^^^^^

.. note::

   This step requires you to have `Node JS v18+ <https://nodejs.org/en>`__ installed.

Open terminal in the ``.vscode/extensions/pygls-playground/`` folder and execute following commands

#. Install dependencies::

   .vscode/extensions/pygls-playground/ $ npm install --no-save

#. Compile the extension::

      .vscode/extensions/pygls-playground/ $ npm run compile

   Alternatively you can run ``npm run watch`` if you are going to be making changes to the extension itself.

Install the Extension
^^^^^^^^^^^^^^^^^^^^^

.. important::

   In order for VSCode to recognise ``pygls-playground`` as a valid extension, you need to complete the build step above **before** opening the *pygls* repository inside VSCode.

   If you did open VSCode before building the extension, you will have to run the ``Developer: Reload Window`` command through the command palette (:kbd:`Ctrl+Shift+P`)

The following steps will depend on your VSCode version

.. tab-set::

   .. tab-item:: VSCode v1.89+

      #. Open your copy of the *pygls* repository in VSCode and goto the :guilabel:`Extensions` tab (:kbd:`Ctrl+Shift+X`)

      #. Find the ``pygls-playground`` extension in the :guilabel:`Recommended` section (not by searching in the marketplace!) and click the :guilabel:`Install Workspace Extension` button.

         **If the button only says "Install", you have not found the right version of the extension**

      #. Make sure that VSCode is using the virtual environment you created during the :ref:`howto-use-pygls-playground-install-pygls` step.

         If necessary, the :guilabel:`Python: Select Interpreter` command can be used to pick a different environment.

         Alternatively, you can set the ``pygls.server.pythonPath`` option in the ``.vscode/settings.json`` file in the repository

   .. tab-item:: VSCode v1.88 and older

      #. Open ``.vscode/extensions/vscode-playground/`` directory in VS Code

      #. The ``pygls-playground`` relies on the `Python extension for VSCode`_ for choosing the appropriate Python environment in which to run the example language servers.

         If you haven't already, you will need to install it and reload the window.

      #. Open the Run and Debug view (:kbd:`Ctrl+Shift+D`)

      #. Select :guilabel:`Launch Client` and press :kbd:`F5`, this will open a second VSCode window with the ``pygls-playground`` extension enabled.

      #. You will need to make sure that VSCode is using the virtual environment you created during the :ref:`howto-use-pygls-playground-install-pygls` step.
         If necessary, the :guilabel:`Python: Select Interpreter` command can be used to pick a different environment.

         Alternatively, you can set the ``pygls.server.pythonPath`` option in the ``.vscode/settings.json`` file


Basic Usage
-----------

By default, the ``pygls-playground`` extension is configured to run the example ``code_actions.py`` server which you can find in the ``examples/servers`` folder of the *pygls* repository.

Try opening the ``examples/servers/workspace/sums.txt`` file.

The playground will automatically start the language server in the background, after a few seconds you should be able to put your cursor on one of the equations and see a code action lightbulb appear.

Open the ``examples/servers/code_actions.py`` file, make a change to the code and save the file.
The playground will detect that the file was changed and automatically restart the server to apply your changes.

Accessing the Server's Logs
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can access the logs for both the client and server in the :guilabel:`pygls` Output Channel

- Run :guilabel:`Output: Show Output Channels...` from the command palette (:kbd:`Ctrl+Shift+P`)
- Select :guilabel:`pygls` from the list

The :guilabel:`Developer: Set Log Level...` command can be used to adjust the verbosity of the log messages.

Calling a Custom Command
^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

   The ``pygls-playground`` can only call custom commands that do not require any arguments

To call a custom :meth:`@server.command <pygls.server.LanguageServer.command>`

- Run :guilabel:`pygls: Execute command` via the command palette (:kbd:`Ctrl+Shift+P`)

- Select your command from the list of options

Configuration
-------------

The settings defined in the ``.vscode/settings.json`` can control most aspects of the playground's behavior.

Selecting a server
^^^^^^^^^^^^^^^^^^

.. tip::

   See :ref:`example-servers` for details on the available servers and which files they work best with.

To select a different server, change the ``pygls.server.launchScript`` setting to the name of the server you wish to run.
This should be a path relative to the ``pygls.server.cwd`` setting.

If everything works as expected, the ``pygls-playground`` extension will default to using the ``examples/servers/`` folder as its working directory.

.. tip::

   Cryptic ``Error: spawn /.../python ENOENT`` messages are often due to the extension using an incorrect working directory.

Debugging a server
^^^^^^^^^^^^^^^^^^

To debug the currently active language server set the ``pygls.server.debug`` option to ``true``.
The server will restart and the debugger connect automatically.

You can control the host and port that the debugger uses through the ``pygls.server.debugHost`` and ``pygls.server.debugPort`` options.

Selecting documents
^^^^^^^^^^^^^^^^^^^

Language servers typically specialise in a relatively small number of file types, so a client will only ask a server about documents it thinks the server is capable of handling.

Most of our example servers are designed to work with ``plaintext``.
To use a server with different set of documents you can modify the ``pygls.client.documentSelector`` option

For example to use a server with ``json`` files

.. code-block:: json

   "pygls.client.documentSelector": [
       {
           "scheme": "file",
           "language": "json"
       },
   ],

You can find the full list of known language identifiers `here <https://code.visualstudio.com/docs/languages/identifiers#_known-language-identifiers>`__.

See the `LSP Specification <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentFilter>`__ for details on all the available options that can be passed to the ``pygls.client.documentSelector`` option.

.. _Python extension for VSCode: https://marketplace.visualstudio.com/items?itemName=ms-python.python
