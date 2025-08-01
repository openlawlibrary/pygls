# Changelog
All notable changes to this project will be documented in this file.


## [2.0.0a6] - 2025-07-18
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a6

### Bug Fixes

- 🐛 fix conversion of client_position into offset_at_position

### CI

- Pin all action versions

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md

### Build

- V2.0.0a6



## [2.0.0a5] - 2025-07-14
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a5

### Bug Fixes

- Utf8 encodings

### CI

- Migrate from `poetry` to `uv`
- Pin all action versions

### Features

- Make `TextDocument.lines` be a `Sequence[str]`
- Provide encoding hint in __repr__

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Re-export get_capability
- More accurate typing
- Lsprotocol 2025.0.0
- Fix indentation
- Add required groups to Makefile
- Update Makefiles to make it easy to switch Python versions

### Refactor

- Use clearer logic for accumulating code unit count

### Testing

- Run slow tests last
- Test position codecs against actual string encoding
- Fix some incorrect utf-8 offsets

### Build

- Bump the pip group across 2 directories with 5 updates
- V2.0.0a5


## [2.0.0a4] - 2025-06-05
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a4

### Bug Fixes

- Update the hello world example to the v2.0 syntax ([#533](https://github.com/openlawlibrary/pygls/issues/533))
- `workspace/executeCommand` with async handlers
- Crash on unknown message ids

### CI

- Start testing on Python 3.14

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Lsprotocol 2025.0.0rc1
- Improve type annotations and docstrings
- Improve type annotations in generated code
- Improve typing of get_capability
- Bump pyodide version
- Add devcontainer and Makefiles

### Testing

- Update error message regex
- Fix pyodide test suite

### Build

- V2.0.0a4

## [2.0.0a3] - 2025-05-18
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a3

### Bug Fixes

- Add fallback JsonRpcException code for malformed server errors ([#520](https://github.com/openlawlibrary/pygls/issues/520))
- Don't cancel the future handling the shutdown request
- Use `issubclass` to check client/server instance
- Error when passing max_workers
- Don't wrap JsonRpcExceptions

### Documentation

- Tweak a comment in client.py ([#521](https://github.com/openlawlibrary/pygls/issues/521))
- Update v2 migration guide
- Remove a surplus `}` in examples/hello-world/README.md ([#523](https://github.com/openlawlibrary/pygls/issues/523))
- Update code lens example command to use type annotations
- Update v2 migration guide

### Features

- Yield to the user's initialize before calculating capabilities
- Use type annotations to parse command arguments

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Fix migration guide link
- Add missing version number
- Fix mypy errors
- Resolve `pytest-asyncio` deprecation warnings

### Refactor

- Unify message handler execution
- Re-implement pygls' builtin handlers using generators

### Testing

- Add test ensuring we can register handlers during `initialize`
- Ensure async user shutdown handlers are executed correctly

### Build

- V2.0.0a3

## [2.0.0a2] - 2024-11-04
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a2

### Bug Fixes

- Use `BinaryIO` not `TextIO` in `start_io()`
- Reduce log noise generated by unimplemented methods
- Return ``None`` for non ``file:`` URIs
- Cancel pending client requests when server process exits
- Wait for the server process to exit
- Don't call sys.exit

### CI

- Run the new pyodide test suite in CI
- Bump action versions

### Documentation

- Add RELEASING.md doc
- Update migration guide to cover thread pool changes
- Remove Strata server implementation
- Update v2 migration guide
- Update migration guide
- Fix intersphinx reference
- Add guide on running the pyodide test suite
- Restructure the documentation... again
- Add guide on running a pyodide server on nodejs
- Add guide on running a pyodide server in the browser

### Features

- Add `start_tcp` method to `JsonRPCClient`
- Add `pygls.cli.start_server`
- Add `start_ws` method to pygls' `LangugageClient`
- Fallback to a synchronous main loop on WASM platforms

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Properly indent RELEASING.md
- Fix task name
- Bump minimum required websockets version
- Update to lsprotocol-2024.0.0b1
- Delete pyodide specific code

### Refactor

- Remove `multiprocessing.pool.ThreadPool`
- Make some methods public
- Convert `aio_readline` function to a `run_async` method
- Use high-level asyncio API in `start_io`
- Use new `pygls.io_` module for pygls' client
- Use high-level asyncio API for `server.start_tcp`
- Use high-level asyncio API for `server.start_ws`
- Stop inheriting from `asyncio.Protocol`
- Rename transport to writer

### Testing

- Add end-to-end test covering threaded handlers
- Simplify coverage reporting
- Add the option to run the end-to-end tests over TCP
- Skip test on Windows for now
- Run end-to-end tests over WebSockets
- Include values for runtime and transport in pytest's header
- Update test cases to align with event loop changes
- Delete the old pyodide test suite
- Add option to run end-to-end tests under pyodide

### Build

- V2.0.0a2

## [2.0.0a1] - 2024-08-24
More details: https://github.com/openlawlibrary/pygls/releases/tag/v2.0.0a1

### Bug Fixes

- Compute `resolve_provider` value for `CodeLensOptions`
- Respect client's preferred encoding when possible
- Compute `prepare_provider` for `RenameOptions`
- Default cwd for local extension
- Compute `resolve_provider` for `DocumentLinkOptions`

### CI

- Update json-extension.yml to align with local extension
- Start testing against Python 3.13
- Stop testing on Python 3.8
- Use Python version in cache key

### Documentation

- Update CONTRIBUTING.md
- Add linter commander to PR template
- Add `sphinx-design` plugin
- Delete getting started guide
- Create a "How To" section
- Add guide on handling invalid data
- Add about section
- Add API Reference section
- Update home page
- Setup basic tutorial structure
- Add how to guide on using the `pygls-playground`
- Add module docstrings for the example servers
- Include the hello world example code directly
- Include the example servers in the documentation
- Add Document Links example server
- Rpm-spec-language-server to Implementations.md
- Update GotoX title
- Add Document and Workspace symbol example server
- Fix typo in `server.py`
- Fix typo in user guide
- Add guide on implementing semantic tokens
- Add example semantic tokens server
- Add draft v2 migration guide

### Features

- Provide more detail in exception
- Update to latest lsprotocol 2024.0.0a2
- Generate server methods from lsp types

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Add README
- Add Kedro VS Code extension into implementations.md
- Update VSCode settings to align with local extension
- Update pygls-playground README
- Update requirements.txt for documentation
- Regen poetry.lock
- Fix lints
- Remove `pathMappings`
- Remove redundant method definitions
- Align to new server implementation
- Align tests with new server implementation
- Rename scripts to `generate_code`
- Add call for testing to README
- Remove deprecated code

### Refactor

- End-to-end test infrastructure
- Update hover.py  example to use language server argument
- Make the playground extension workspace local
- Rely on the `pygls.server.cwd` setting
- Use generated `BaseLanguageServer`
- Rename `Server` to `JsonRPCServer`

### Testing

- Add end-to-end test for `textDocument/hover` requests
- Add end-to-end tests for color related methods
- Add end-to-end tests for various "Goto X" methods
- Add end-to-end tests for `textDocument/codeLens`
- Add end-to-end tests for the different diagnostic approaches
- Add end-to-end tests for the various formatting requests
- Extend `get_client_for` to accept custom capabilities
- Add end-to-end tests for rename methods
- Add end-to-end semantic tokens test

### Build

- Upgrade black to latest (24.3.0)
- Bump idna from 3.6 to 3.7
- Bump jinja2 from 3.1.3 to 3.1.4
- Requests from 2.31.0 to 2.32.0
- Bump idna from 3.6 to 3.7 in /docs
- Bump certifi from 2023.11.17 to 2024.7.4
- Bump requests from 2.31.0 to 2.32.2 in /docs
- Bump urllib3 from 2.1.0 to 2.2.2
- Bump jinja2 from 3.1.2 to 3.1.4 in /docs
- Bump zipp from 3.17.0 to 3.19.1
- Bump setuptools from 69.0.2 to 70.0.0 in /docs

## [1.3.1] - 2024-03-26
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.3.1

### Documentation

- Add systemd-language-server to implementations
- Update implementations.md with Chapel's language server

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Apache license missing dash

### Build

- V1.3.1

## [1.3.0] - 2024-01-29
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.3.0

### Bug Fixes

- Add missing value to `pygls.trace.server`

### CI

- Don't let Pyodide test fail the whole build
- Don't trigger CI on both push and pull_request

### Features

- Drop Python 3.7 support
- Update dependencies to latest(ish)
- Enable debugging of servers in the playground

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Cattrs is a direct dependency
- Update pytest-asyncio
- Add pytest-lsp and lsp-devtools to Implementations.md
- Update lsprotocol to 2023.0.1

### Build

- V1.3.0

## [1.2.1] - 2023-11-30
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.2.1

### Bug Fixes

- Handle ResponseErrors correctly

### Miscellaneous Tasks

- Update CHANGELOG.md
- Clean CHANGELOG

### Build

- V1.2.1

## [1.2.0] - 2023-11-18
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.2.0

### Bug Fixes

- Remove dependency on typeguard
- Linting and formatting issues
- Simplify option validation check
- Index error on empty workspace

### Features

- Allow user to override Python interpreter

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Update `poetry.lock` after removing typeguard
- Add example configuration
- Pin lsprotocol to 2023.0.0

### Refactor

- Move workspace/ into servers/ dir

## [1.1.2] - 2023-10-28
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.1.2

### Documentation

- Correct doc comment for PositionCodec.client_num_units

### Miscellaneous Tasks

- Update CHANGELOG.md
- Update CONTRIBUTORS.md
- Split protocol.py into own folder/files

### Build

- Bump urllib3 from 2.0.6 to 2.0.7
- Allow installation with typeguard 4.x
- V1.1.2

## [1.1.1] - 2023-10-06
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.1.1

### Bug Fixes

- Prevent AttributeError root_path when no workspace

### CI

- Fix release process

### Miscellaneous Tasks

- Manual changes for v1.1.0 release
- Explicit exports from pygls.workspace

### Build

- Bump urllib3 from 2.0.5 to 2.0.6
- V1.1.1

## [1.1.0] - 2023-10-02
More details: https://github.com/openlawlibrary/pygls/releases/tag/v1.1.0

### Bug Fixes

- Fix broken link and outdated comment

- Correctly cast from UTF16 positions
- Ensure server commands can be executed
- Mypy lints
- Error code of JsonRpcInternalError
- Only show code action when there's no sum
- Don't include trailing whitespace in code action title
- 'bool' object has no attribute 'resolve_provider'
- Computation of formatting and diagnostic provider capabilities

### CI

- Migrate to Poetry and modernise
- Linter for conventional commits
- Autogenerate changelog with `git-cliff`
- Automate CONTRIBUTORS.md
- Retry Pyodide tests
- Test against Python 3.12
- Use `matrix.python-version` in cache key
- Update json-extension pipeline
- Pin poetry to 1.5.1
- Do not install chromium/chromedriver
- Enable coverage reporting
- Run all lints even when some fail
- Increase Pyodide CI retries to 6

### Documentation

- Use autodoc to document client methods
- Update docstrings
- Change specification for commit messages
- Typo in vscode-playground README.md
- Add api docs for servers, protocol and workspace
- Align docstring formatting
- Handle methods starting with `$/`
- Update links and code snippets
- Rename advanced usage to user guide
- Instructions for using plain text files with vscode-playground

### Features

- Add document diagnostic capability
- Add workspace symbol resolve
- Add workspace diagnostic support
- Adds inline value support
- Adds type hierarchy request support
- Add `await` syntax support for sending edit request to client
- Allow servers to provide `NotebookDocumentSyncOptions`
- Initial support for notebook document syncronisation
- Add notebook support to example `inlay_hints.py` server
- Accept `PositionEncoding` client capability
- Support UTF32 ans UTF8 position encoding

### Miscellaneous Tasks

- Update autogenerated Pygls client
- Introduce `black` formatting
- Add `.git-blame-ignore-revs` file
- Delete fountain-vscode-extension
- Update README.md
- Bump lsprotocol version
- Fix deprecation warning, set chrome path
- Disable body-max-line-length check
- Add .readthedocs.yaml
- Strict types in uris.py and workspace.py
- Move workspace/doc/position into own files
- Fix mypy types
- Maintain `Workspace` backwards compat
- Fix use of deprecated methods in tests/test_language_server.py

### Refactor

- Move example json-server to `examples/servers`
- Rename `json-vscode-extension/` -> `vscode-playground`
- Simplify end-to-end test client fixture definition
- Rename `Client` -> `JsonRPCClient`
- Rename `LanguageClient` -> `BaseLanguageClient`
- Rename `<verb>_document` to `<verb>_text_document`
- Expose workspace via a property
- Server `Position` class
- Rename server Position to PositionCodec, instantiate it in Workspace
- Reference types via `types` module
- Make `default` argument mandatory, add type annotations

### Testing

- Test that the client provided token is used
- Remove a useless sleep
- Test cases of server initiated progress
- Base Pyodide wheel deps off poetry.lock

### Build

- Bump semver in /examples/fountain-vscode-extension
- Bump semver in /examples/json-vscode-extension
- Bump word-wrap in /examples/json-vscode-extension
- Lock min Python version to 3.7.9
- Cache specific Python minor version
- Bump lsprotocol to 2023.0.0b1
- Release v1.1.0

### Json-extension

- Support cancellation in progress example

### Progress

- Support work done progress cancellation from client

### Server

- Add a type annotation to help completions in editor

### Extra Notes
#### Added

- Add `LanguageClient` with LSP methods autogenerated from type annotations in `lsprotocol` ([#328])
- Add base JSON-RPC `Client` with support for running servers in a subprocess and communicating over stdio. ([#328])
- Support work done progress cancel ([#253])
- Add support for `textDocument/inlayHint` and `inlayHint/resolve` requests ([#342])

#### Changed
#### Fixed

- `pygls` no longer overrides the event loop for the current thread when given an explicit loop to use. ([#334])
- Fixed `MethodTypeNotRegisteredError` when registering a `TEXT_DOCUMENT_DID_SAVE` feature with options. ([#338])
- Fixed detection of `LanguageServer` type annotations when using string-based annotations. ([#352])

[#328]: https://github.com/openlawlibrary/pygls/issues/328
[#334]: https://github.com/openlawlibrary/pygls/issues/334
[#338]: https://github.com/openlawlibrary/pygls/discussions/338
[#253]: https://github.com/openlawlibrary/pygls/pull/253
[#342]: https://github.com/openlawlibrary/pygls/pull/342
[#304]: https://github.com/openlawlibrary/pygls/issues/304

# Pre Automation Changelog

## [1.0.2] - May 15th, 2023
### Changed
- Update typeguard to 3.x ([#327])

[#327]: https://github.com/openlawlibrary/pygls/issues/327


### Fixed
- Data files are no longer placed inside the wrong `site-packages` folder when installing `pygls` ([#232])
[#232]: https://github.com/openlawlibrary/pygls/issues/232


## [1.0.1] - February 16th, 2023
### Fixed

 - Fix progress example in json extension. ([#230])
 - Fix `AttributeErrors` in `get_configuration_async`, `get_configuration_callback`, `get_configuration_threaded` commands in json extension. ([#307])
 - Fix type annotations for `get_configuration_async` and `get_configuration` methods on `LanguageServer` and `LanguageServerProtocol` objects ([#307])
 - Provide `version` param for publishing diagnostics ([#303])
 - Relaxed the Python version upper bound to `<4` ([#318])

[#230]: https://github.com/openlawlibrary/pygls/issues/230
[#303]: https://github.com/openlawlibrary/pygls/issues/303
[#307]: https://github.com/openlawlibrary/pygls/issues/307
[#318]: https://github.com/openlawlibrary/pygls/issues/318

## [1.0.0] - 2/12/2022
### Changed
BREAKING CHANGE: Replaced `pydantic` with [`lsprotocol`](https://github.com/microsoft/lsprotocol)

## [0.13.1] - 1/12/2022
### Changed
Docs now state that the v1 alpha branch is the recommended way to start new projects
### Fixed
Support `CodeActionKind.SourceFixAll`

## [0.13.0] - 2/11/2022
### Added
- Add `name` and `version` arguments to the constructor of `LanguageServer` ([#274])
### Changed
- Default behaviour change: uncaught errors are now sent as `showMessage` errors to client.
  Overrideable in `LanguageServer.report_server_error()`: https://github.com/openlawlibrary/pygls/pull/282
### Fixed
- `_data_recevied()` JSONRPC message parsing errors now caught
- Fix "Task attached to a different loop" error in `Server.start_ws` ([#268])

[#274]: https://github.com/openlawlibrary/pygls/issues/274
[#268]: https://github.com/openlawlibrary/pygls/issues/268

## [0.12.4] - 24/10/2022
### Fixed
- Remove upper bound on Pydantic when Python is <3.11

## [0.12.3] - 24/10/2022
### Fixed
- Require Pydantic 1.10.2 when Python is 3.11

## [0.12.2] - 26/09/2022
### Fixed
- Relaxed the Python version upper bound to `<4` ([#266])

[#266]: https://github.com/openlawlibrary/pygls/pulls/266

## [0.12.1] - 01/08/2022
### Changed
- `Document` objects now expose a text document's `language_id`
- Various Pyodide improvements
- Improved tests for more reliable CI

## [0.12] - 04/07/2022

### Added

- Allow custom word matching for `Document.word_at_point`

### Changed

- Upgraded Python support to 3.10, dropping support for 3.6
- Dependency updates, notably Pydantic 1.9 and Websockets 10

### Fixed

## [0.11.3] - 11/06/2021

### Added

### Changed

- Update json-example to include an example semantic tokens method ([#204])

### Fixed

- Fix example extension client not detecting debug mode appropriately ([#193])
- Fix how the `semantic_tokens_provider` field of `ServerCapabilities` is computed ([#213])

[#193]: https://github.com/openlawlibrary/pygls/issues/193
[#204]: https://github.com/openlawlibrary/pygls/issues/204
[#213]: https://github.com/openlawlibrary/pygls/pulls/213

## [0.11.2] - 07/23/2021

### Added

### Changed

### Fixed

- Fix feature manager ([#203])
- Use `127.0.0.1` for tests and examples to avoid Docker issues ([#165])

[#203]: https://github.com/openlawlibrary/pygls/issues/203
[#165]: https://github.com/openlawlibrary/pygls/issues/165

## [0.11.1] - 06/21/2021

### Added

### Changed

- Remove defaults from all optional fields on protocol-defined types ([#198])

### Fixed

[#198]: https://github.com/openlawlibrary/pygls/pull/198

## [0.11.0] - 06/18/2021

### Added

- Testing against Python 3.9 ([#186])
- Websocket server implementation `start_websocket` for LSP ([#129])

### Changed

### Fixed

[#186]: https://github.com/openlawlibrary/pygls/pull/186
[#129]: https://github.com/openlawlibrary/pygls/pull/129

## [0.10.3] - 05/05/2021

### Added

### Changed

- Move from Azure Pipelines to Github Actions ([#182] & [#183])
- Update json-example ([#175])
- Relax text_doc type to VersionedTextDocumentIdentifier ([#174])

### Fixed

- Handle `BrokenPipeError` on shutdown ([#181])
- Exit when no more data available ([#178])
- Adding kind field to resource file operation types ([#177])
- Don't install the tests to site-packages ([#169])
- Don't serialize unwanted `"null"` values in server capabilities ([#166])

[#183]: https://github.com/openlawlibrary/pygls/pull/183
[#182]: https://github.com/openlawlibrary/pygls/pull/182
[#181]: https://github.com/openlawlibrary/pygls/pull/181
[#178]: https://github.com/openlawlibrary/pygls/pull/178
[#177]: https://github.com/openlawlibrary/pygls/pull/177
[#175]: https://github.com/openlawlibrary/pygls/pull/175
[#174]: https://github.com/openlawlibrary/pygls/pull/174
[#169]: https://github.com/openlawlibrary/pygls/pull/169
[#166]: https://github.com/openlawlibrary/pygls/pull/166

## [0.10.2] - 03/25/2021

### Added

### Changed

- Handle lost connection; Remove psutil ([#163])

### Fixed

- Fix `pydantic` Unions type conversion ([#160])
- Fix change_notifications type (pydantic bug) ([#158])

[#163]: https://github.com/openlawlibrary/pygls/pull/163
[#160]: https://github.com/openlawlibrary/pygls/pull/160
[#158]: https://github.com/openlawlibrary/pygls/pull/158

## [0.10.1] - 03/17/2021

### Fixed

- Remove "query" from FoldingRangeParams ([#153])

[#153]: https://github.com/openlawlibrary/pygls/pull/153

## [0.10.0] - 03/16/2021

### Added

- New LSP types and methods ([#139])
- `pydantic` and `typeguard` deps for type-checking ([#139])
- Runtime type matching and deserialization ([#139])

### Changed

- New LSP types and methods ([#139])
- Updated docs ([#139])

### Fixed

- Periodically check client pid and exit server ([#149])
- Fix server handling of client errors ([#141])

[#149]: https://github.com/openlawlibrary/pygls/pull/149
[#141]: https://github.com/openlawlibrary/pygls/pull/141
[#139]: https://github.com/openlawlibrary/pygls/pull/139

## [0.9.1] - 09/29/2020

### Added

- Functions to convert positions from and to utf-16 code units ([#117])
- Type definitions for `ClientInfo` and `HoverParams` ([#125])

### Changed

- Exit server normally when `ctrl+c` is pressed in command shell.
- Mark deprecated `rangeLength` optional in `TextDocumentContentChangeEvent` ([#123])
- Optimize json-rpc message serialization ([#120])
- Fix `__init__()` constructors in several interface types ([#125])
- Fix valueSet type in `SymbolKindAbstract` ([#125])

### Fixed

- `coroutine` deprecation warning - use async def instead ([#136])

[#125]: https://github.com/openlawlibrary/pygls/pull/125
[#123]: https://github.com/openlawlibrary/pygls/pull/123
[#120]: https://github.com/openlawlibrary/pygls/pull/120
[#117]: https://github.com/openlawlibrary/pygls/pull/117
[#136]: https://github.com/openlawlibrary/pygls/pull/136

## [0.9.0] - 04/20/2020

### Changed

- Fixed missing `Undo` member from `FailureHandlingKind` in types ([#98])
- Fixed `@command`, `@feature` and `@thread` decorators to retain type of wrapped functions ([#89])

### Added

- _Azure Pipelines_ build script ([#100] and [#103])
- Run tests and linters on multiple python versions with _tox_ ([#100])
- Use python enums in types module ([#92])
- Add comparisons and repr support to Range and Location types ([#90])

### Removed

- _appveyor_ build script ([#103])

[#103]: https://github.com/openlawlibrary/pygls/pull/103
[#100]: https://github.com/openlawlibrary/pygls/pull/100
[#98]: https://github.com/openlawlibrary/pygls/pull/98
[#92]: https://github.com/openlawlibrary/pygls/pull/92
[#90]: https://github.com/openlawlibrary/pygls/pull/90
[#89]: https://github.com/openlawlibrary/pygls/pull/89

## [0.8.1] - 09/05/2019

### Changed

- Fix parsing of partial messages and those with Content-Length keyword ([#80])
- Fix Full SyncKind for servers accepting Incremental SyncKind ([#78])

[#80]: https://github.com/openlawlibrary/pygls/pull/80
[#78]: https://github.com/openlawlibrary/pygls/pull/78

## [0.8.0] - 05/13/2019

### Added

- Add new types and features from LSP v3.14.0 ([#67])
- Add API to dynamically register/unregister client capability ([#67])
- Full text document synchronization support ([#65])
- Add more tests for `deserialize_message` function ([#61])

### Changed

- Response object should contain result OR error field ([#64])
- Fix handling parameters whose names are reserved by Python ([#56])

[#67]: https://github.com/openlawlibrary/pygls/pull/67
[#65]: https://github.com/openlawlibrary/pygls/pull/65
[#64]: https://github.com/openlawlibrary/pygls/pull/64
[#61]: https://github.com/openlawlibrary/pygls/pull/61
[#56]: https://github.com/openlawlibrary/pygls/pull/56

## [0.7.4] - 03/21/2019

### Added

- Add Pull Request template ([#54])

### Changed

- Update dependencies ([#53])
- Fix initialization failure when no workspace is open ([#51])

[#54]: https://github.com/openlawlibrary/pygls/pull/54
[#53]: https://github.com/openlawlibrary/pygls/pull/53
[#51]: https://github.com/openlawlibrary/pygls/pull/51

## [0.7.3] - 01/30/2019

### Added

- Add _flake8_ and _bandit_ checks to _appveyor_ script

### Changed

- Start using [Keep a Changelog][keepachangelog] format.
- Fix and refactor _initialize_ LSP method and add more tests
- Fix _python 3.5_ compatibility
- Use _python 3.5_ in _appveyor_ script

## 0.7.2 - 12/28/2018

- Fix README to use absolute paths for GitHub urls (needed for PyPi)

## 0.7.1 - 12/28/2018

- Add `publish_diagnostics` to LanguageServer
- Fix validation function in json example
- Correct advanced usage doc page
- "pygls" -> _pygls_ everywhere in the docs

## 0.7.0 - 12/21/2018

- Open source _pygls_

## 0.6.0

- Modules/functions/methods reorganization
- Add more features/commands to json-extension example
- Add unit tests to json-extension example
- Update `appveyor.yml`
- Small bug fixes

## 0.5.0

- Return awaitable Future object from get_configuration
- Add / Remove Workspace folders bugfix
- Attach loop to child watcher for UNIX systems

## 0.4.0

- Gracefully shutdown and exit server process
- Disallow requests after shutdown request is received
- Added more types for type hints
- Improved example

## 0.3.0

- Async functions (coroutines) support
- Mark function to execute it in a thread pool
- Added _lsp_ types
- New example
- Fixed `appveyor.yml`

## 0.2.0

- Added classes for `textDocument/completion` method response

## 0.1.0

- Initial Version

[keepachangelog]: https://keepachangelog.com/en/1.0.0/
[semver]: https://semver.org/spec/v2.0.0.html

[Unreleased]: https://github.com/openlawlibrary/pygls/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/openlawlibrary/pygls/compare/v0.13.1...v1.0.0
[0.13.1]: https://github.com/openlawlibrary/pygls/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/openlawlibrary/pygls/compare/v0.12.3...v0.13.0
[0.12.4]: https://github.com/openlawlibrary/pygls/compare/v0.12.3...v0.12.4
[0.12.3]: https://github.com/openlawlibrary/pygls/compare/v0.12.2...v0.12.3
[0.12.2]: https://github.com/openlawlibrary/pygls/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/openlawlibrary/pygls/compare/v0.12...v0.12.1
[0.12]: https://github.com/openlawlibrary/pygls/compare/v0.11.3...v0.12
[0.11.3]: https://github.com/openlawlibrary/pygls/compare/v0.11.2...v0.11.3
[0.11.2]: https://github.com/openlawlibrary/pygls/compare/v0.11.1...v0.11.2
[0.11.1]: https://github.com/openlawlibrary/pygls/compare/v0.11.0...v0.11.1
[0.11.0]: https://github.com/openlawlibrary/pygls/compare/v0.10.3...v0.11.0
[0.10.3]: https://github.com/openlawlibrary/pygls/compare/v0.10.2...v0.10.3
[0.10.2]: https://github.com/openlawlibrary/pygls/compare/v0.10.1...v0.10.2
[0.10.1]: https://github.com/openlawlibrary/pygls/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/openlawlibrary/pygls/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/openlawlibrary/pygls/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/openlawlibrary/pygls/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/openlawlibrary/pygls/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/openlawlibrary/pygls/compare/v0.7.4...v0.8.0
[0.7.4]: https://github.com/openlawlibrary/pygls/compare/v0.7.3...v0.7.4
[0.7.3]: https://github.com/openlawlibrary/pygls/compare/v0.7.2...v0.7.3
