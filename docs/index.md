# pygls

_pygls_ (pronounced like "spy glass") is generic implementation of [Language Server Protocol](https://microsoft.github.io/language-server-protocol/specification) written in Python programming language. It allows you to write your own [Language Server](https://langserver.org/) in just few lines of code.

## Features

- cross-platform support
- TCP/IP and IO communication
- run in asyncio event loop
- register LSP features and custom commands as:
  - asynchronous functions (coroutines)
  - synchronous functions
  - functions that will be executed in separate thread
- thread management
- in-memory workspace with incremental document updates
- good test coverage

## Python versions

_pygls_ works with Python 3.5+.
