# Compiled JSON Language Server Example

## Server compilation dependencies

Compiling the server's Python code is done using
[Nuitka](https://nuitka.net/doc/user-manual.html) in this example, but as long as your
tool of choice results in an executable that accepts the right arguments, you should be
fine. To install Nuitka, please follow the
[instructions](https://nuitka.net/doc/user-manual.html#installation).

Remember that Nuitka itself depends on some installation of (mingw with) gcc, so don't
skip that part of the install!


## Running the Example

1. Run ``make install`` in this folder.
1. Open VS Code on this folder.
1. Press Ctrl+Shift+B to compile the client and server.
    - Make sure you add a script to activate the correct python environment with pygls
      and nuitka in ./.vscode/tasks.json for the server compilation. (before ``make
      clean && make server``)
1. Make the executable at ``./dist/json_server/json_server`` available to the extension
   with one of these options:
    1. Set a ``jsonServer.serverPath`` to the absolute path to the executable.
    1. Search for "changing the PATH environment variable" online if you don't know how
       to do this.
1. Press Ctrl+Shift+D to run a debugging instance of VS Code with the extension loaded.


## Separate server compilation

The server can be compiled separately using ``make server``. Compilation results can be
cleaned up using ``make clean``. These commands should work on both Windows as well as
Linux machines using the ``make.bat`` and ``Makefile`` files in this folder.


## Running with development server

To speed up development, you can skip compilation by setting the
``jsonServer.serverPath`` and ``jsonServer.serverArgs`` differently in the User or
Workspace Settings of your (Development Host of) VS Code:

1. Set ``jsonServer.serverPath`` to your development environment's Python executable
   which should have ``pygls`` installed.
1. Set ``jsonServer.serverArgs`` to ``["-m", "path/to/json_server.py"]``.

With these settings, re-triggering the extension activation should reload (or more
precisely: re-run) the latest ``json_server.py`` directly. For an absolute clean slate,
you can restart your debug session or reload the VS Code window you want to use:

1. Press Ctrl+Shift+P
1. Type "reload" and/or select "Developer: Reload Window".
