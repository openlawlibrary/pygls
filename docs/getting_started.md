# Getting started

This document explains how to install and get started writing Language Servers that are based on pygls.

---

## Installation

To get the latest release from PyPI, simply run:

```console
pip install pygls
```

Alternatively, pygls source code can be downloaded from our [GitHub](https://github.com/openlawlibrary/pygls) page and installed with following command:

```console
python setup.py install
```

## Quick start

Pygls is a language server framework that can be started without writing any additional code:

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_tcp('localhost', 8080)
```

After running the code above, server will start listening for incoming `Json RPC` requests on `http://localhost:8080`.

## Build-in features

Pygls comes with following predefined set of `Language Server Protocol` (LSP) features:

- [initialize](https://microsoft.github.io/language-server-protocol/specification#initialize) request is sent as a first request from client to the server to setup their communication. Pygls automatically computes registered LSP capabilities and send them as part of `InitializeResult`

- [shutdown](https://microsoft.github.io/language-server-protocol/specification#shutdown) request is sent from the client to the server and asks the server to shut down.

- [exit](https://microsoft.github.io/language-server-protocol/specification#exit) notification is sent from client to the server and asks server to exit the process. Pygls automatically release all resources and stops the process.

- [textDocument/didOpen](https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen) notification will tell pygls to create a document in the in-memory workspace which can be accessed later.

- [textDocument/didChange](https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange) notification will tell pygls to update the document source. For now, pygls supports just incremental document changes.

- [textDocument/didClose](https://microsoft.github.io/language-server-protocol/specification#textDocument_didClose) notification will tell pygls to remove a document from the in-memory workspace.

- [workspace/didChangeWorkspaceFolders](https://microsoft.github.io/language-server-protocol/specification#workspace_didChangeWorkspaceFolders) notification will tell pygls to update in-memory workspace folders.

## User defined features

Pygls comes with API for registering additional features like `code completion`, `find all references`, `go to definition`, etc...

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

... as well as [custom commands](change_link):

```python
@server.command('myVerySpecialCommandName')
def cmd_return_hello_world(ls, *args):
    return 'Hello World!'
```

Features that are currently supported by the LSP specification can be found in [pygls.features](https://github.com/openlawlibrary/pygls/blob/master/pygls/features.py) module, while corresponding request/response classes can be found in [pygls.types](https://github.com/openlawlibrary/pygls/blob/master/pygls/types.py) module.

## Advanced usage

To reveal the full potential of pygls (`thread management`, `coroutines`, `multi-root workspace`, `TCP/IO communication` etc.) keep on reading the docs.

## Try the examples

Take a look at [Json Extension](https://github.com/openlawlibrary/pygls/tree/master/examples/json-extension) and follow the [README file](https://github.com/openlawlibrary/pygls/blob/master/examples/README.md) to install and use it.
