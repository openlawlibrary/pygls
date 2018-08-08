# pygls examples

This folder contains various examples of pygls language server:

- `simple-json` - Language server which validates json after document is saved.

- `multi-root` - Language server which reads the configuration from the client before validating document.
    Example shows how the pygls `LanguageServer` can be inherited and started.

## Debug examples

- TODO: correct

### Run Server

1. Open root directory in VS Code
1. Open debug view (`ctrl + shift + D`).
1. Select `Launch {Multi-root|Simple-JSON} server` and press `F5`.

### Run Client

1. Open `vscode-client` for each example in a terminal instance and run `npm install`.
1. Select `Launch {Multi-root|Simple-JSON} server` and press `F5`.
