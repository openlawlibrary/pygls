importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js")

/* @ts-ignore */
import * as languageServer from "./server.py";

async function initPyodide() {

    console.log("Initializing pyodide.")

    /* @ts-ignore */
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/"
    })

    console.log("Installing dependencies.")
    await pyodide.loadPackage(["micropip"])
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('pygls')

        # Uncomment to use a local build of pygls
        # await micropip.install('https://xxx.loca.lt/out/pygls-<version>-py3-none-any.whl')
    `)

    console.log("Loading server.")
    await pyodide.runPythonAsync(languageServer)

    return pyodide
}

const pyodideReady = initPyodide()

/* @ts-ignore */
self.post_message = (json_string) => {

    // Uncomment to see messages sent from the language server
    // console.log(json_string)

    let obj = JSON.parse(json_string)
    postMessage(obj)
}

onmessage = async (event) => {
    let pyodide = await pyodideReady

    /* @ts-ignore */
    self.client_message = JSON.stringify(event.data)
    const response = await pyodide.runPythonAsync(`
        from js import client_message

        # Uncomment to see the messages sent from the client
        # print(client_message)

        message = json.loads(client_message, object_hook=deserialize_message)
        server.lsp._procedure_handler(message)
    `)
}
