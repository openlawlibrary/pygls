importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js")

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
        import json
        import sys
        import micropip

        #await micropip.install('pygls')

        # Uncomment to use a local build of pygls
        await micropip.install('./pygls-0.14.1.dev0+gf21ad06.d20221112-py3-none-any.whl')
    `)

    console.log("Loading server.")

    // Patch stdout to redirect the output.
    pyodide.globals.get('sys').stdout.write = patchedStdout
    return pyodide
}

async function reloadServer(pyodide, serverCode) {
    await pyodide.runPythonAsync(`
${serverCode}

server.start_pyodide()
`)
}

const pyodidePromise = initPyodide()

onmessage = async (event) => {
    let pyodide = await pyodidePromise

    let msg = event.data
    if (msg.type === 'reload') {
        console.log(msg.code)
        reloadServer(pyodide, msg.code)
        return
    }

    /* @ts-ignore */
    self.client_message = JSON.stringify(msg)
    await pyodide.runPythonAsync(`
        from js import client_message

        message = json.loads(client_message, object_hook=server.lsp._deserialize_message)
        server.lsp._procedure_handler(message)
    `)
}

