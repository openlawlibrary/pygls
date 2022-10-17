# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keepachangelog],
and this project adheres to [Semantic Versioning][semver].

## [Unreleased]
### Added

- Add `name` and `version` arguments to the constructor of `LanguageServer` ([#274])

[#274]: https://github.com/openlawlibrary/pygls/issues/274

### Changed
- Default behaviour change: uncaught errors are now sent as `showMessage` errors to client.
  Overrideable in `LanguageServer.report_server_error()`: https://github.com/openlawlibrary/pygls/pull/282
### Fixed
- `_data_recevied()` JSONRPC message parsing errors now caught

## [0.12.4] - 24/10/2022
### Fixed
- Remove upper bound on Pydantic when Python is <3.11

## [0.12.3] - 24/10/2022
### Fixed
- Require Pydantic 1.10.2 when Python is 3.11

## [1.0.0alpha] - 17/10/2022
### Changed
🚧 Alpha Code (likely contains bugs) 🚧
BREAKING CHANGE: Replaced `pydantic` with [`lsprotocol`](https://github.com/microsoft/lsprotocol)

## [0.12.2] - 26/09/2022
### Fixed
- Relaxed the Python version upper bound to `<4`
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

- Update json-example to include an example semantic tokens method ([204])

### Fixed

- Fix example extension client not detecting debug mode appropriately ([#193])
- Fix how the `semantic_tokens_provider` field of `ServerCapabilities` is computed ([213])

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

[Unreleased]: https://github.com/openlawlibrary/pygls/compare/v0.12...HEAD
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
