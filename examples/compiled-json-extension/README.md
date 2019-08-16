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
1. Press Ctrl+Shift+D to run a debugging instance of VS Code with the extension loaded.


## Separate server compilation

The server can be compiled separately using ``make server``. Compilation results can be
cleaned up using ``make clean``. These commands should work on both Windows as well as
Linux machines using the ``make.bat`` and ``Makefile`` files in this folder.
