# pygls examples

This folder contains various examples of pygls language server:

- `simple-json-server` - Language server which validates json after document is saved.

- `multi-root-server` - Language server which reads the configuration from the client before validating document.
    Example shows how the pygls `LanguageServer` can be inherited and started.

## Debug examples

### Run Server

1. Open root directory in VS Code
2. Open debug view (`ctrl + shift + D`), choose example from dropdown and press `F5`

### Run Client

1. Open vscode-client in a new vs code instance
2. Open terminal and run `npm install`
3. Build `CTRL + SHIFT + B`
4. Run `F5`
