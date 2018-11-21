# Advanced usage

## Language server

Language server is responsible for receiving and sending messages over the Language Server Protocol which is based on [_Json RPC_ protocol](https://www.jsonrpc.org/specification).

### Connections

_pygls_ supports **TCP** and socket **IO** types of connections.

#### TCP

TCP connections are usually used while developing the Language Server. This way server can be started in _debug_ mode separately and wait for client connection.

_NOTE_: Server should be started **before** the client.

Code snippet bellow shows how to start the server in _TCP_ mode.

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_tcp('localhost', 8080)
```

#### IO

IO connections are useful when client is starting the server as a child process and usually this is the way to go in production.

Code snippet bellow shows how to start the server in _IO_ mode.

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_io()
```

### Logging

Logs are useful for tracing client requests, finding out errors and measuring time needed to return results to the client.

_pygls_ uses builtin python _logging_ module which has to be configured before server is started.  

Official documentation about logging in python can be found [here](https://docs.python.org/3/howto/logging-cookbook.html), and bellow is the minimal setup to setup logging in _pygls_:

```python
import logging
from pygls.server import LanguageServer

logging.basicConfig(filename='pygls.log', filemode='w', level=logging.DEBUG)

server = LanguageServer()

server.start_io()
```

## Features

What is feature in _pygls_? In terms of Language Servers and Language Server Protocol, by feature we mean one of the predefined methods from LSP [specification](https://microsoft.github.io/language-server-protocol/specification), such as: _code completion_, _formatting_, _code lens_, etc. Features that are available can be found in [pygls.features](path_to_feature) module.

## Commands

Commands can be treated as a _custom features_, i.e. everything that is not covered by LSP specification, but needs to be implemented.

## API

This section contains _in-depth_ explanation how to use _pygls_ API.

### _Feature_ and _command_ advanced registration

_pygls_ is a language server which relies on _asyncio event loop_. It is _asynchronously_ listening for incoming messages and, depending on the way method is registered, applying different execution strategies to respond to the client.

Depending on the use case, _features_ and _commands_ can be registered in three different ways.

To make sure that you fully understand what is happening under the hood, please take a look at the example [server](../examples/json-extension/server/server.py) and test it following the [instructions](../examples/README.md).

#### _asynchronous_ functions (_coroutines_)

_pygls_ supports `python 3.5+` which has a keyword `async` to specify coroutines.

Code bellow shows how to register a coroutine command:

```python
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(10):
        ls.workspace.show_message("Counting down... {}".format(10 - i))
        await asyncio.sleep(1)
```

Registering coroutine _feature_ is exactly the same.

Coroutines are executed in _pygls_'s _event loop_.

**IMPORTANT**: Using computation intensive operations will _block_ the main thread and should be _avoided_ inside coroutines. Take a look at [_threaded_ functions](#threaded-functions) for more details.

#### _synchronous_ functions

#### _threaded_ functions

### Notifications

### Configuration

### Workspace
