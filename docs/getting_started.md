# Getting started

This document explains how to install and get started writing Language servers that are based on _pygls_.

---

## Installation

To get the latest release from PyPI, simply run:

```console
pip install pygls
```

Alternatively, _pygls_ source code can be downloaded from our [GitHub](https://github.com/openlawlibrary/pygls) page and installed with following command:

```console
python setup.py install
```

## Quick start

### Spin the server up

_pygls_ is a language server framework that can be started without writing any additional code:

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_tcp('localhost', 8080)
```

After running the code above, server will start listening for incoming `Json RPC` requests on `http://localhost:8080`.

### Register features and commands

_pygls_ comes with API for registering additional features like `code completion`, `find all references`, `go to definition`, etc...

```python
@server.feature(COMPLETION, trigger_characters=[','])
def completions(params: CompletionParams):
    """Returns completion items."""
    return CompletionList(False, [
        CompletionItem('Item1'),
        CompletionItem('Item2'),
        CompletionItem('Item3'),
    ])
```

... as well as custom commands:

```python
@server.command('myVerySpecialCommandName')
def cmd_return_hello_world(ls, *args):
    return 'Hello World!'
```

Features that are currently supported by the LSP specification can be found in [pygls.features](../pygls/features.py) module, while corresponding request/response classes can be found in [pygls.types](../pygls/types.py) module.

## Advanced usage

To reveal the full potential of _pygls_ (`thread management`, `coroutines`, `multi-root workspace`, `TCP/IO communication` etc.) keep on reading the docs.

## Try the examples

Take a look at [Json Extension](../examples/json-extension) and follow the [README file](../examples/README.md) to install and try it out.
