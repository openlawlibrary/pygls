.. _howto-use-pyodide:

How To Run a Server in Pyodide
==============================

.. highlight:: none

`Pyodide <https://pyodide.org/en/stable/>`__ provides a version of the CPython interpreter compiled for WebAssembly, allowing you to execute Python programs either in a web browser or in NodeJS.

This guide outlines how to run your *pygls* server in such an environment.

.. important::

   This environment imposes some `restrictions and limitations <https://pyodide.org/en/stable/usage/wasm-constraints.html>`__ to consider.
   The most obvious restrictions are:

   - only the STDIO method of communication is supported
   - threads are unavailable, so your server cannot use the :meth:`@server.thread() <pygls.server.JsonRPCServer.thread>` decorator
   - while it *is* possible to use async-await syntax in Pyodide, *pygls* does not currently enable it by default.

The setup is slightly different depending on if you are running your server via the :ref:`Browser <howto-use-pyodide-in-browser>` or :ref:`NodeJs <howto-use-pyodide-in-node>`

.. _howto-use-pyodide-in-node:

Using NodeJS
------------

The most likely use case for using NodeJS is testing that your server works in Pyodide without requiring the use of a browser testing tool like `Selenium <https://www.selenium.dev/>`__.
In fact, this is how we test that *pygls* works correctly when running under Pyodide.

To help illustrate the steps required, we will use pygls' test suite as an example.

.. tip::

   You can find the complete setup in the `tests/pyodide <https://github.com/openlawlibrary/pygls/tree/main/tests/pyodide>`__ folder of the pygls repository.

Writing our Python code as normal, each server is executed with the help of a wrapper script::

  $ node run_server.js /path/to/server.py

The simplest wrapper script might look something like the following

.. code-block:: javascript

   const fs = require('fs');
   const { loadPyodide } = require('pyodide');

   async function runServer(serverCode) {
       // Initialize pyodide.
       const pyodide = await loadPyodide()

       // Install dependencies
       await pyodide.loadPackage("micropip")
       const micropip = pyodide.pyimport("micropip")
       await micropip.install("pygls")

       // Run the server
       await pyodide.runPythonAsync(serverCode)
   }

   if (process.argv.length < 3) {
       console.error("Missing server.py file")
       process.exit(1)
   }

   // Read the contents of the given `server.py` file.
   const serverCode = fs.readFileSync(process.argv[2], 'utf8')

   runServer(serverCode).then(() => {
       process.exit(0)
   }).catch(err => {
       process.exit(1);
   })

The above code is assuming that the given Python script ends with a call to your server's :meth:`~pygls.server.JsonRPCServer.start_io` method.

Redirecting Output
^^^^^^^^^^^^^^^^^^

Unfortunately, if you tried the above script you will find that your language client wouldn't be able to establish a connection with the server.
This is due to fact Pyodide will print some log messages to ``stdout`` interfering with the client's communication with the server::

  Loading micropip, packaging
  Loaded micropip, packaging
  Loading attrs, six
  Loaded attrs, six
  ...

To work around this in ``run_server.js`` we create a function that will write to a log file.

.. code-block:: javascript

   const consoleLog = console.log
   const logFile = fs.createWriteStream("pyodide.log")

   function writeToFile(...args) {
       logFile.write(args[0] + `\n`);
   }

And we use it to temporarily override ``console.log`` during startup

.. code-block:: javascript

   async function runServer(serverCode) {
       // Annoyingly, while we can redirect stderr/stdout to a file during this setup stage
       // it doesn't prevent `micropip.install` from indirectly writing to console.log.
       //
       // Internally, `micropip.install` calls `pyodide.loadPackage` and doesn't expose loadPackage's
       // options for redirecting output i.e. messageCallback.
       //
       // So instead, we override console.log globally.
       console.log = writeToFile
       const pyodide = await loadPyodide({
           // stdin:
           stderr: writeToFile,
       })

       await pyodide.loadPackage("micropip")
       const micropip = pyodide.pyimport("micropip")
       await micropip.install("pygls")

       // Restore the original console.log
       console.log = consoleLog
       await pyodide.runPythonAsync(serverCode)
   }

While we're redirecting output, we may as well also pass the ``writeToFile`` function to pyodide's ``stderr`` channel.
That way we're also able to see the server's logging output while it's running!

.. important::

   Since node's ``fs`` API is asynchronous, don't forget to only start the server once the log file has been opened!

   .. code-block:: javascript

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

Workspace Access
^^^^^^^^^^^^^^^^

.. seealso::

   - :external+pyodide:std:doc:`usage/file-system`
   - :external+pyodide:std:ref:`accessing_files_quickref`

At this point we're able to get a server up and running however, it wouldn't be able to access any files!
There are many ways to approach exposing your files to the server (see the above resources), but for the pygls test suite we copy them into Pyodide's in-memory filesystem before starting the server.

.. code-block:: javascript

   const path = require('path')
   const WORKSPACE = path.join(__dirname, "..", "..", "examples", "servers", "workspace")

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

   async function runServer() {
     // ...
     loadWorkspace(pyodide)
     // ...
   }

It's important to note that this **WILL NOT** synchronise any changes made within the Pyodide runtime back to the source filesystem, but for the purpose of pygls' test suite it is sufficient.

It's also important to note that your language client will need to send URIs that make sense to server's environment i.e. ``file:///workspace/sums.txt`` and not ``file:///home/username/Projects/pygls/examples/servers/workspace/sums.txt``.

.. _howto-use-pyodide-in-browser:

Using the Browser
-----------------
