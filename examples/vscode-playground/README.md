# Pygls Playground

![Screenshot of the vscode-playground extension in action](https://user-images.githubusercontent.com/2675694/260591942-b7001a7b-3081-439d-b702-5f8a489856db.png)

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

1. Install pygls
   ```
   python -m pip install -e .
   ```

### Install Client Dependencies

Open terminal in the same directory as this file and execute following commands:

1. Install node dependencies

   ```
   npm install
   ```
1. Compile the extension

   ```
   npm run compile
   ```
   Alternatively you can run `npm run watch` if you are going to be actively working on the extension itself.

### Run Extension

1. Open this directory in VS Code

1. The playground relies on the [Python extension for VSCode](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for choosing the appropriate Python environment in which to run the example language servers.
   If you haven't already, you will need to install it and reload the window.

1. Open the Run and Debug view (`ctrl + shift + D`)

1. Select `Launch Client` and press `F5`, this will open a second VSCode window with the `vscode-playground` extension enabled.

1. You will need to make sure that VSCode ia using a virtual environment that contains an installation of `pygls`. 
   The `Python: Select Interpreter` command can be used to pick the correct one

   If you see a window like the following

   ![Screenshot of the VSCode workspace folder selection dialog](https://user-images.githubusercontent.com/2675694/262779751-367c568e-37d7-490a-b83e-910da1596298.png)

   be sure to select the one corresponding with the `pygls/examples/workspace` folder.
