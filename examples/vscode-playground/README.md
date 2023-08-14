# Pygls Playground

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
1. Open debug view (`ctrl + shift + D`)
1. Select `Launch Client` and press `F5`
