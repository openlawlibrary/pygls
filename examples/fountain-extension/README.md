# Fountain Language Server

This is an example [web extension](https://code.visualstudio.com/api/extension-guides/web-extensions) that can be used with online versions of VSCode such as [github.dev](https://github.dev/openlawlibrary/pygls) and [vscode.dev](https://vscode.dev/github/openlawlibrary/pygls). 

## Install Dependencies

Open terminal and execute following commands:

1. `npm install`

## Run Example

Getting a local instance of an extension into the online version of VSCode isn't the simplest task, but the following steps based on [this guide](https://code.visualstudio.com/api/extension-guides/web-extensions#test-your-web-extension-in-on-vscode.dev) you should be able to get it up and running.

1. Open a terminal and run 

   ```
   $ npm run watch
   ```

   This starts [webpack](https://webpack.js.org/) which compiles the files in `src/` and place the results in the `out/` directory, webpack will then listen for changes to any of the `src/` files and automatically recompile. 

1. In a second terminal run

   ```
   $ npm run serve 

   > fountain-lsp-web@ serve /home/alex/Projects/blog/code/fountain-lsp-web
   > npx serve --cors -l 5000

   npx: installed 88 in 6.613s

   ┌──────────────────────────────────────────────────┐
   │                                                  │
   │   Serving!                                       │
   │                                                  │
   │   - Local:            http://localhost:5000      │
   │   - On Your Network:  http://192.168.0.31:5000   │
   │                                                  │
   │   Copied local address to clipboard!             │
   │                                                  │
   └──────────────────────────────────────────────────┘   
   ```
   This starts a simple web server and makes the extension available over a HTTP connection.

1. Finally, in a third terminal run 

   ```
   $ npm run tunnel

   > fountain-lsp-web@ tunnel /.../pygls/examples/fountain-extension
   > npx localtunnel -p 5000

   npx: installed 22 in 3.043s
   your url is: https://xxxx-yyyy-zzzz.loca.lt
   ```

   This does... magic 🤷 that makes the extension available over a HTTPS connection.
   
1. However, to enable the connection you must first visit the URL above in your web browser and click the `Click to Continue` button.

   ![tunnel.png](./tunnel.png)

1. With the setup out of the way you can now open [github.dev](https://github.dev/openlawlibrary/pygls) or [vscode.dev](https://vscode.dev/github/openlawlibrary/pygls) in your favourite web browser. 
Hit `F1` to open the command palette and choose the `Developer: Install Web Extension...` command, paste in the URL from above and hit enter.

1. Finally open a `*.fountain` file and try out the language server! 
   **Tip:** If you'd like some more visibility into the workings of the extension you can open the developer tools with `F12` to see the console messages.

   ![demo.png](./demo.png)
## Using the development version of `pygls`

If you need to test local changes to the `pygls` library you can change the `initPyodide` code to install a local build of `pygls` instead of the one available on PyPi

1. `python -m pip install build`
1. `python -m build`
1. `cp dist/pygls-<version>-py3-none-any.whl examples/fountain-extension/out/`
1. In `./src/server.ts` change the call to `micropip` to install you dev build of `pygls`
   ```ts
       await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('https://xxxx-yyyy-zzzz.loca.lt/out/pygls-<version>-py3-none-any.whl')
    `)
   ```