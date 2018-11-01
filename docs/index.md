# Pygls

Pygls (pronounced like "spy glass") is generic implementation of 
[Language Server Protocol](https://microsoft.github.io/language-server-protocol/specification)
written in Python. It allows you to write your own Python based
[Language Server](https://langserver.org/) in just few lines of code.

## Features

- cross-platform support
- TCP/IP and IO communication
- running in asyncio event loop
- register LSP features and custom commands as:
  - asynchronous functions (coroutines)
  - synchronous functions
  - functions that will be executed in separate thread
- thread management
- in-memory workspace with incremental document updates
- good test coverage

## Python versions

Pygls works with Python 3.5+.

## Examples

- [json-extension](https://github.com/openlawlibrary/pygls/tree/master/examples/json-extension) - Simple extension for json documents based on pygls
