# Advanced usage

## Language server

Language server is responsible for receiving and sending messages over the `Language Server Protocol` which is based on [_Json RPC_ protocol](https://www.jsonrpc.org/specification).

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

What is a feature in _pygls_? In terms of Language servers and `Language Server Protocol`, by feature we mean one of the predefined methods from LSP [specification](https://microsoft.github.io/language-server-protocol/specification), such as: _code completion_, _formatting_, _code lens_, etc. Features that are available can be found in [pygls.features](../features) module.

### _Built-in_ features

_pygls_ comes with following predefined set of `Language Server Protocol` (LSP) features:

- [initialize](https://microsoft.github.io/language-server-protocol/specification#initialize) request is sent as a first request from client to the server to setup their communication. _pygls_ automatically computes registered LSP capabilities and sends them as part of `InitializeResult` response.

- [shutdown](https://microsoft.github.io/language-server-protocol/specification#shutdown) request is sent from the client to the server to ask the server to shutdown.

- [exit](https://microsoft.github.io/language-server-protocol/specification#exit) notification is sent from client to the server to ask the server to exit the process. _pygls_ automatically releases all resources and stops the process.

- [textDocument/didOpen](https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen) notification will tell _pygls_ to create a document in the in-memory workspace which will exist as long as document is opened in editor.

- [textDocument/didChange](https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange) notification will tell _pygls_ to update the document text. For now, _pygls_ supports **only** incremental document changes.

- [textDocument/didClose](https://microsoft.github.io/language-server-protocol/specification#textDocument_didClose) notification will tell _pygls_ to remove a document from the in-memory workspace.

- [workspace/didChangeWorkspaceFolders](https://microsoft.github.io/language-server-protocol/specification#workspace_didChangeWorkspaceFolders) notification will tell _pygls_ to update in-memory workspace folders.

## Commands

Commands can be treated as a _custom features_, i.e. everything that is not covered by LSP specification, but needs to be implemented.

## API

This section contains _in-depth_ explanation how to use _pygls_ API.

### _Feature_ and _command_ advanced registration

_pygls_ is a language server which relies on _asyncio event loop_. It is _asynchronously_ listening for incoming messages and, depending on the way method is registered, applying different execution strategies to respond to the client.

Depending on the use case, _features_ and _commands_ can be registered in three different ways.

To make sure that you fully understand what is happening under the hood, please take a look at the example [server](../examples/json-extension/server/server.py) and test it following the [instructions](../examples/README.md).

_NOTE_: It is possible to register features that are already _built-in_ and it will be called immediately after them.

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

_Threaded_ functions are just regular functions, but marked with _pygls_'s `thread` decorator:

```python
# Decorator order is not important in this case
@json_server.thread()
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    # Omitted
```

_pygls_ uses its own _thread pool_ to execute above function in _daemon_ thread and it is _lazy_ initialized first time when function market with `thread` decorator is fired.

Use _threaded_ functions to run blocking operations, but make sure that you understand python's `multithreading` and [GIL](https://en.wikipedia.org/wiki/Global_interpreter_lock) before messing with threads.

### Notifications

Notification is a request message without `id` field and server _must not_ reply to it. This means that, if your language server received the notification, even if you return result inside your handler function, the result won't be passed to the client.

`Language Server Protocol`, unlike `Json RPC`, allows bidirectional communication between the server and the client.

#### Configuration

[Configuration](https://microsoft.github.io/language-server-protocol/specification#workspace_configuration) request is sent from the server to the client in order to fetch configuration settings from the client. When the requested configuration is collected, the client sends data as a notification to the server.

_NOTE_: Although `configuration` is a `request`, it is explained in this section because the client sends back the `notification` object.

Code snippet bellow shows how to send configuration to the client:

```python
def get_configuration(self,
                      params: ConfigurationParams,
                      callback: Optional[Callable[[List[Any]], None]] = None
                      ) -> asyncio.Future:
    # Omitted
```

_pygls_ has three ways for handling configuration notification from the client, depending on way how the function is registered (described [here](#Feature-and-command-advanced-registration)):

- _asynchronous_ functions (_coroutines_)

```python
# await keyword tells event loop to switch to another task until notification is received
config = await ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')]))
```

- _synchronous_ functions

```python
# callback is called when notification is received
def callback(config):
    # Omitted

config = ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')]), callback)
```

- _threaded_ functions

```python
# .result() will block the thread
config = ls.get_configuration(ConfigurationParams([ConfigurationItem('doc_uri_here', 'section')])).result()
```

#### Show message

[Show message](https://microsoft.github.io/language-server-protocol/specification#window_showMessage) is notification that is sent from the server to the client to display text message.

Code snippet bellow shows how to send show message notification:

```python
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    for i in range(10):
        # Sends message notification to the client
        ls.workspace.show_message("Counting down... {}".format(10 - i))
        await asyncio.sleep(1)
```

#### Show message log

[Show message log](https://microsoft.github.io/language-server-protocol/specification#window_logMessage) is notification that is sent from the server to the client to display text message in the output channel.

Code snippet bellow shows how to send show message log notification:

```python
@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    for i in range(10):
        # Sends message log notification to the client's output channel
        ls.workspace.show_message_log("Counting down... {}".format(10 - i))
        await asyncio.sleep(1)
```

#### Publish diagnostics

[Publish diagnostics](https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics) notifications are sent from the server to the client to signal results of validation runs.

Usually this notification is sent after document is opened, or on document content change, e.g.:

```python
@json_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.workspace.show_message("Text Document Did Open")
    ls.workspace.show_message_log("Validating json...")

    # Get document from workspace
    text_doc = ls.workspace.get_document(params.textDocument.uri)

    diagnostic = Diagnostic(
                     range=Range(Position(line-1, col-1), Position(line-1, col)),
                     message="Custom validation message",
                     source="Json Server"
                 )

    # Send diagnostics
    ls.workspace.publish_diagnostics(text_doc.uri, [diagnostic])
```

#### Custom notifications

_pygls_ supports sending custom notifications to the client and bellow is method declaration for this functionality:

```python
def send_notification(self, method: str, params: object = None) -> None:
    # Omitted
```

And method invocation sample:

```python
server.send_notification('myCustomNotification', 'test data')
```

### Workspace

[Workspace](../pygls/workspace.py) is a python object that holds information about workspace folders, opened documents and has the logic for updating document content.

_pygls_ automatically take care about mentioned features of the workspace.

Workspace methods that can be used for user defined features are:

- Get document from the workspace

```python
    def get_document(self, doc_uri: str) -> Document:
        # Omitted
```

- [Apply edit](https://microsoft.github.io/language-server-protocol/specification#workspace_applyEdit) request

```python
def apply_edit(self, edit: WorkspaceEdit, label: str = None) -> ApplyWorkspaceEditResponse:
    # Omitted
```
