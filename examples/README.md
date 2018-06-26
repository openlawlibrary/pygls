# pygls examples

This folder contains various examples of pygls language server:

- `simple-json-server` - Language server which validates json after document is saved.

- `multi-root-server` - Language server which reads the configuration from the client before validating document.
    Example shows how the pygls `LanguageServer` can be inherited and started.

## Debug examples

1. Add `python.pythonPath` to your workspace settings file
2. From `examples` directory, run `python install_pygls.py`
3. Open debug view (`ctrl + shift + D`), choose example from dropdown and press F5
4. Run `npm install` in vscode-client directory
5. Open vscode-client in new vs code instance
6. Press `CTRL + SHIFT + B`
7. Press F5
