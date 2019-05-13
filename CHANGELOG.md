# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keepachangelog],
and this project adheres to [Semantic Versioning][semver].

## [Unreleased]

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

- Open source  _pygls_

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

[Unreleased]: https://github.com/openlawlibrary/pygls/compare/v0.8.0...HEAD
[0.8.0]: https://github.com/openlawlibrary/pygls/compare/v0.7.4...v0.8.0
[0.7.4]: https://github.com/openlawlibrary/pygls/compare/v0.7.3...v0.7.4
[0.7.3]: https://github.com/openlawlibrary/pygls/compare/v0.7.2...v0.7.3
