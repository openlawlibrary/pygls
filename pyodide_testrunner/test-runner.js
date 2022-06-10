importScripts("https://cdn.jsdelivr.net/pyodide/v0.20.0/full/pyodide.js")

// Used to redirect pyodide's stdout to the webpage.
function patchedStdout(...args) {
    postMessage(args[0])
}

async function runTests(whl) {
    console.log("Loading pyodide")
    let pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.20.0/full/"
    })

    console.log("Installing dependencies")
    await pyodide.loadPackage("micropip")
    await pyodide.runPythonAsync(`
        import sys
        import micropip

        await micropip.install('pytest')
        await micropip.install('pytest-asyncio')
        await micropip.install('${whl}')
    `)

    console.log('Running testsuite')

    // Patch stdout to redirect the output.
    pyodide.globals.get('sys').stdout.write = patchedStdout
    await pyodide.runPythonAsync(`
        import pytest
        exit_code = pytest.main(['--color', 'no', '--pyargs', 'pygls.tests'])
    `)

    postMessage({ exitCode: pyodide.globals.get('exit_code') })
}

let queryParams = new URLSearchParams(self.location.search)
runTests(queryParams.get('whl'))
