# Pygls Playground

![Screenshot of the pygls-playground extension in action](https://user-images.githubusercontent.com/2675694/260591942-b7001a7b-3081-439d-b702-5f8a489856db.png)

This VSCode extension aims to serve two purposes.

- Provide an environment in which you can easily experiment with the pygls framework by trying some of our example servers - or by writing your own

- Provide a minimal example of what it takes to integrate a pygls powered language server into VSCode.

For an example of a more complete VSCode client, including details on how to bundle your Python code with the VSCode extension itself you may also be interested in Microsoft's [template extension for Python tools](https://github.com/microsoft/vscode-python-tools-extension-template).

## Setup

### Install Server Dependencies

Open a terminal in the repository's root directory

1. Create a virtual environment
   ```
   python -m venv env
   ```

1. Activate the environment
   ```
   source ./env/bin/activate
   ```

1. Install `pygls`
   ```
   python -m pip install -e .
   ```

### Install Client Dependencies

Open terminal in the same directory as this file and execute following commands:

1. Install node dependencies

   ```
   npm install --no-save
   ```
1. Compile the extension

   ```
   npm run compile
   ```
   Alternatively you can run `npm run watch` if you are going to be actively working on the extension itself.

### Run Extension (VSCode v1.89+)

> [!IMPORTANT]
> In order for VSCode to recognise `pygls-playground` as a valid extension, you need to complete the setup steps above **before** opening this repo inside VSCode.
> If you opened VSCode before compiling the extension, you will have to run the `Developer: Reload Window` command through the command palette (`Ctrl+Shift+P`)

1. Open the `pygls` repository in VSCode

1. Goto the `Extensions` tab (`Ctrl+Shift+X`), find the `pygls-playground` extension in the *Recommended* section (not by searching in the marketplace!) and click the `Install Workspace Extension` button.
   **If the button only says "Install", you've not found the right version of this extension**

1. You will need to make sure that VSCode is using a virtual environment that contains an installation of `pygls`.
   The `Python: Select Interpreter` command can be used to pick the correct one.

   Alternatively, you can set the `pygls.server.pythonPath` option in the `.vscode/settings.json` file

### Run Extension (VSCode v1.88 and older)

1. Open this directory in VS Code

1. The playground relies on the [Python extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for choosing the appropriate Python environment in which to run the example language servers.
   If you haven't already, you will need to install it and reload the window.

1. Open the Run and Debug view (`ctrl + shift + D`)

1. Select `Launch Client` and press `F5`, this will open a second VSCode window with the `pygls-playground` extension enabled.

1. You will need to make sure that VSCode is using a virtual environment that contains an installation of `pygls`.
   The `Python: Select Interpreter` command can be used to pick the correct one.

   Alternatively, you can set the `pygls.server.pythonPath` option in the `.vscode/settings.json` file

## Configuration

By default, the `pygls-playground` extension is configured to run the example `code_actions.py` server which you can find in the `examples/servers` folder of this repository.
(For best results, try opening the `examples/servers/workspace/sums.txt` file).

However, the `.vscode/settings.json` file in this repository can be used alter this and more.

### Selecting a server

> [!TIP]
> See the [README](../../../examples/servers/README.md) in the `examples/servers` folder for details on the available servers and which files they work best with.

To select a different example server, change the `pygls.server.launchScript` setting to the name of the server you wish to run

### Selecting the working directory

> [!TIP]
> Cryptic `Error: spawn /.../python ENOENT` messages are often due to the extension using an incorrect working directory.

If everything works as expected, the `pygls-playground` extension **should** default to using the `examples/servers/` folder as its working directory.

If this is not the case, or you want to change it to something else, you can change the `pygls.server.cwd` option

### Selecting documents

Language servers typically specialise in a relatively small number of file types, so a client will only ask a server about documents

The `code_actions.py` example is intended to be used with `plaintext` files (e.g. the provided `sums.txt` file). To use a server with different file types you can modify the `pygls.client.documentSelector` option

For example to use a server with `json` files:

```
"pygls.client.documentSelector": [
    {
        "scheme": "file",
        "language": "json"
    },
],
```

You can find the full list of known language identifiers [here](https://code.visualstudio.com/docs/languages/identifiers#_known-language-identifiers).

See the [LSP Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#documentFilter) for details on all the available options that can be passed to the `pygls.client.documentSelector` option.

### Debugging the server

To debug the language server set the `pygls.server.debug` option to `true`.
The server should be restarted and the debugger connect automatically.

You can control the host and port that the debugger uses through the `pygls.server.debugHost` and `pygls.server.debugPort` options.
