# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog][keepachangelog],
and this project adheres to [Semantic Versioning][semver].

## [Unreleased]

### Changed

- Start using [Keep a Changelog][keepachangelog] format.

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
