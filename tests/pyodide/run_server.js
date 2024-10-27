const fs = require('fs');
const path = require('path')
const { loadPyodide } = require('pyodide');

const consoleLog = console.log

const WORKSPACE = path.join(__dirname, "..", "..", "examples", "servers", "workspace")
const DIST = path.join(__dirname, "..", "..", "dist")

// Create a file to log pyodide output to.
const logFile = fs.createWriteStream("pyodide.log")

function writeToFile(...args) {
    logFile.write(args[0] + `\n`);
}

// Load the workspace into the pyodide runtime.
//
// Unlike WASI, there is no "just works" solution for exposing the workspace/ folder
// to the runtime - it's up to us to manually copy it into pyodide's in-memory filesystem.
function loadWorkspace(pyodide) {
    const FS = pyodide.FS

    // Create a folder for the workspace to be copied into.
    FS.mkdir('/workspace')

    const workspace = fs.readdirSync(WORKSPACE)
    workspace.forEach((file) => {
      try {
        const filename = "/" + path.join("workspace", file)
        // consoleLog(`${file} -> ${filename}`)

        const stream = FS.open(filename, 'w+')
        const data = fs.readFileSync(path.join(WORKSPACE, file))

        FS.write(stream, data, 0, data.length, 0)
        FS.close(stream)
      } catch (err) {
        consoleLog(err)
      }
    })
}

// Find the *.whl file containing the build of pygls to test.
function findWhl() {
    const files = fs.readdirSync(DIST);
    const whlFile = files.find(file => /pygls-.*\.whl/.test(file));

    if (whlFile) {
        return path.join(DIST, whlFile);
    } else {
        consoleLog("Unable to find whl file.")
        throw new Error("Unable to find whl file.");
    }
}

async function runServer(serverCode) {
    // Annoyingly, while we can redirect stderr/stdout to a file during this setup stage
    // it doesn't prevent `micropip.install` from indirectly writing to console.log.
    //
    // Internally, `micropip.install` calls `pyodide.loadPackage` and doesn't expose loadPacakge's
    // options for redirecting output i.e. messageCallback.
    //
    // So instead, we override console.log globally.
    console.log = writeToFile
    const pyodide = await loadPyodide({
        // stdin:
        stderr: writeToFile,
    })

    loadWorkspace(pyodide)

    await pyodide.loadPackage("micropip")
    const micropip = pyodide.pyimport("micropip")
    await micropip.install(`file://${findWhl()}`)

    // Restore the original console.log
    console.log = consoleLog
    await pyodide.runPythonAsync(serverCode)
}

if (process.argv.length < 3) {
    console.error("Missing server.py file")
    process.exit(1)
}


const serverCode = fs.readFileSync(process.argv[2], 'utf8')

logFile.once('open', (fd) => {
    runServer(serverCode).then(() => {
        logFile.end();
        process.exit(0)
    }).catch(err => {
        logFile.write(`Error in server process\n${err}`)
        logFile.end();
        process.exit(1);
    })
})
