# Advanced usage

## Language server

Language server is responsible for receiving and sending messages over the Language Server Protocol which is based on [_Json RPC_ protocol](https://www.jsonrpc.org/specification).

### Connections

_pygls_ supports **TCP** and socket **IO** types of connections.

#### TCP

TCP connections are usually used while developing the Language server. This way server can be started in _debug_ mode separately and wait for client connection.

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

_pygls_ uses built-in python _logging_ module which has to be configured before server is started.  

Official documentation about logging in python can be found [here](https://docs.python.org/3/howto/logging-cookbook.html), and bellow is the minimal setup to setup logging in _pygls_:

```python
import logging

from pygls.server import LanguageServer

logging.basicConfig(filename='pygls.log', filemode='w', level=logging.DEBUG)

server = LanguageServer()

server.start_io()
```

## Features

What is a feature in _pygls_? In terms of Language servers and Language Server Protocol, by feature we mean one of the predefined methods from LSP [specification](https://microsoft.github.io/language-server-protocol/specification), such as: _code completion_, _formatting_, _code lens_, etc. Features that are available can be found in [pygls.features](../features) module.

### _Built-in_ features

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

Code snippet bellow shows how to register a command as a coroutine:

```python
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    # Omitted
```

Registering _feature_ as a coroutine is exactly the same.

Coroutines are functions that are executed as tasks in _pygls_'s _event loop_. They should contain at least one _await_ expression (more about [awaitables](https://docs.python.org/3.5/glossary.html#term-awaitable)) which tells event loop to switch to another task while waiting. This allows _pygls_ to listen for client requests in a _non blocking_ way, while still only running in the _main_ thread.

Tasks can be canceled by the client if they didn't start executing (see [Cancellation Support](https://microsoft.github.io/language-server-protocol/specification#cancelRequest)).

**IMPORTANT NOTE**: Using computation intensive operations will _block_ the main thread and should be _avoided_ inside coroutines. Take a look at [_threaded_ functions](#threaded-functions) for more details.

#### _synchronous_ functions

Synchronous functions are regular functions which _blocks_ the _main_ thread until they are executed.

[Built-in features](#Built-in-features) are registered as regular functions to ensure correct state of language server initialization and workspace.

Code snippet bellow shows how to register a command as a regular function:

```python
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    # Omitted
```

Registering _feature_ as a regular function is exactly the same.

**IMPORTANT NOTE**: Using computation intensive operations will _block_ the main thread and should be _avoided_ inside regular functions. Take a look at [_threaded_ functions](#threaded-functions) for more details.

#### _threaded_ functions



### Notifications

### Configuration

### Workspace
