# pygls

## a pythonic generic language server _(pronounce like "spy glass")_

A generic implementation of the [Language Server Protocol][1] for use as a foundation for writing language servers using Python (e.g. Python, XML, etc.).

[1]: https://microsoft.github.io/language-server-protocol/

## Setup

Install `pygls` using following command `pip install .` from the project's root.

If you are using virtual environment (VE), then follow next steps:

1. Open terminal, create and activate VE ([see how](https://docs.python.org/3/tutorial/venv.html))
2. In the same terminal, navigate to project root directory and run `pip install .` command (be sure that VE is activated)

### Run tests

1. `pip install .[test]`
2. Open terminal, navigate to tests directory and run `pytest` command
