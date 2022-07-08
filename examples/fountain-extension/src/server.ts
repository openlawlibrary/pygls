importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js")

/* @ts-ignore */
import * as languageServer from "./server.py";

function patchedStdout(data) {
    if (!data.trim()) {
        return
    }

    // Uncomment to see messages sent from the language server
    // console.log(data)
    postMessage(JSON.parse(data))
}

async function initPyodide() {

    console.log("Initializing pyodide.")

    /* @ts-ignore */
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/"
    })

    console.log("Installing dependencies.")
    await pyodide.loadPackage(["micropip"])
    await pyodide.runPythonAsync(`
        import sys
        import micropip
        await micropip.install('pygls')

        # Uncomment to use a local build of pygls
        # await micropip.install('https://xxx.loca.lt/out/pygls-<version>-py3-none-any.whl')
    `)

    console.log("Loading server.")

    // Patch stdout to redirect the output.
    pyodide.globals.get('sys').stdout.write = patchedStdout
    await pyodide.runPythonAsync(languageServer)

    return pyodide
}

const pyodideReady = initPyodide()

onmessage = async (event) => {
    let pyodide = await pyodideReady

    // Uncomment to see messages from the client
    // console.log(event.data)

    /* @ts-ignore */
    self.client_message = JSON.stringify(event.data)
    await pyodide.runPythonAsync(`
        from js import client_message

        message = json.loads(client_message, object_hook=deserialize_message)
        server.lsp._procedure_handler(message)
    `)
}
