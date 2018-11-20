# Advanced usage

## Language server



### Connections

_pygls_ supports **TCP** and socket **IO** types of connections.

#### TCP

TCP connections are usually used while developing the Language Server. This way server can be started in _debug_ mode.

NOTE: Server should be started **before** the client.

Code snippet bellow shows how to start the server in TCP mode.

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_tcp('localhost', 8080)
```

#### IO

IO connections are useful when client is starting the server as a child process.

Code snippet bellow shows how to start the server in IO mode.

```python
from pygls.server import LanguageServer

server = LanguageServer()

server.start_io()
```

### Logging

Logs are useful for tracing client requests, finding out errors and measuring time needed to return results to the client.

_pygls_ uses builtin python _logging_ module which has to be configured before server startup.  

Official documentation about logging in python can be found [here](https://docs.python.org/3/howto/logging-cookbook.html), and bellow is the minimal setup to get _pygls_ logs:

```python
import logging

logging.basicConfig(filename='pygls.log', filemode='w', level=logging.DEBUG)
```

## Features

What is feature in _pygls_? In terms of Language Servers and Language Server Protocol, by feature we mean one of the predefined methods from LSP [specification](https://microsoft.github.io/language-server-protocol/specification), such as: _code completion_, _formatting_, _code lens_, etc.

## Commands

Commands can be treated as a _custom features_, i.e. everything that is not covered by LSP specification, but is needed by the client.

## API

## Notifications

## Configuration

## Workspace
