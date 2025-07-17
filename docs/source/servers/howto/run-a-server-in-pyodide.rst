.. _howto-use-pyodide:

How To Run a Server with Pyodide
================================

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

.. seealso::

   `monaco-languageclient <https://github.com/TypeFox/monaco-languageclient>`__ GitHub repository
       For plenty of examples on how to build an in-browser client on top of the `monaco editor <https://microsoft.github.io/monaco-editor/>`__

   `This commit <https://github.com/openlawlibrary/pygls/pull/291/commits/166afdf8387fd7074af6ffadf62d6002caab3527>`__
      For an (outdated!) example on building a simple language client for pygls servers in the browser.

Getting your pygls server to run in a web browser using Pyodide as the runtime *is possible*.
Unfortunately, it is not necessarily *easy* - mostly because you will most likely have to build your own language client at the same time!

While building an in-browser language client is beyond the scope of this article, we can provide some suggestions to get you started - and if you figure out a nicer way please let us know!

WebWorkers
^^^^^^^^^^

Running your language server in the browser's main thread is not a great idea since any time your server is processing some message it will block the UI.
Instead we can run the server in a `WebWorker <https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers>`__, which we can think of as the browser's version of a background thread.

Using the `monaco-editor-wrapper <https://github.com/TypeFox/monaco-languageclient/tree/main/packages/wrapper>`__ project, connecting your server to the client can be as simple as a few lines of configuration

.. code-block:: typescript

   import '@codingame/monaco-vscode-python-default-extension';
   import { MonacoEditorLanguageClientWrapper, UserConfig } from 'monaco-editor-wrapper'

   export async function run(containerId: string) {
     const wrapper = new MonacoEditorLanguageClientWrapper()
     const userConfig: UserConfig = {
       wrapperConfig: {
         editorAppConfig: {
           $type: 'extended',
           codeResources: {
             main: {
               text: '1 + 1 =',
               uri: '/workspace/sums.txt',
               enforceLanguageId: 'plaintext'
             }
           }
         }
       },
       languageClientConfig: {
         languageId: 'plaintext',
         options: {
           $type: 'WorkerDirect',
           worker: new Worker('/run_server.js')
         },
       }
     }

     const container = document.getElementById(containerId)
     await wrapper.initAndStart(userConfig, container)
   }

Where ``run_server.js`` is a slightly different version of the wrapper script we used for the NodeJS section above.

Overview
^^^^^^^^

.. seealso::

   :external+pyodide:std:doc:`usage/webworker`


Unlike all the other ways you will have run a pygls server up until now, the client and server will not be communicating by reading/writing bytes to/from each other.
Intead they will be passing JSON objects directly using the ``onmessage`` event and ``postMessage`` functions.
As a result, we will not be calling one of the server's ``start_xx`` methods either, instead we will rely on the events we receive from the client "drive" the server.

.. raw:: html

   <svg width="100%" height="200" viewBox="0 0 300 150" xmlns="http://www.w3.org/2000/svg">
     <g transform="translate(-50, 0)">
       <rect x="20" y="50" width="100" height="50" fill="#D3EAF9" stroke="#2A6EAB" />
       <text x="50" y="80" font-family="Arial" font-size="14" fill="#2A6EAB">Client</text>

       <rect x="280" y="50" width="100" height="50" fill="#F9EAD3" stroke="#AB6E2A" />
       <text x="310" y="80" font-family="Arial" font-size="14" fill="#AB6E2A">Server</text>

       <line x1="120" y1="70" x2="280" y2="70" stroke="#2A6EAB" stroke-width="2" marker-end="url(#arrowhead)" />
       <text x="170" y="65" font-family="Arial" font-size="12" fill="#2A6EAB">onmessage</text>

       <line x1="280" y1="85" x2="120" y2="85" stroke="#AB6E2A" stroke-width="2" marker-end="url(#arrowhead)" />
       <text x="170" y="105" font-family="Arial" font-size="12" fill="#AB6E2A">postMessage</text>

       <defs>
         <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
           <polyline points="1,1 5,5 1,9" fill="none" stroke="context-stroke" stroke-width="1" />
         </marker>
       </defs>
     </g>
   </svg>


Also note that since our server code is running in a WebWorker, we will need to use the `importScripts <https://developer.mozilla.org/en-US/docs/Web/API/WorkerGlobalScope/importScripts>`__ function to pull in the Pyodide library.

.. code-block:: typescript

   importScripts("https://cdn.jsdelivr.net/pyodide/<pyodide_version>/full/pyodide.js");

   async function initPyodide() {
       // TODO
   }

   const pyodidePromise = initPyodide()

   onmessage = async (event) => {
       let pyodide = await pyodidePromise
       // TODO
   }

By awaiting ``pyodidePromise`` in the ``onmessage``, we ensure that Pyodide and all our server code is ready before attempting to handle any messages.

Initializing Pyodide
^^^^^^^^^^^^^^^^^^^^

The ``initPyodide`` function is fairly similar to the ``runServer`` function from the NodeJS example above.
The main differences are

- We are now redirecting ``stderr`` to ``console.log`` rather than a file
- We are now also redirecting ``stdout``, parsing the JSON objects being written out and passing them to the ``postMessage`` function to send them onto the client.
- We **are not** calling ``server.start_io`` in our server init code.

.. code-block:: typescript

   async function initPyodide() {
       console.log("Initializing pyodide.")

       /* @ts-ignore */
       let pyodide = await loadPyodide({
         stderr: console.log
       })

       console.log("Installing dependencies.")
       await pyodide.loadPackage(["micropip"])
       await pyodide.runPythonAsync(`
           import micropip
           await micropip.install('pygls')
       `)

       // See https://pyodide.org/en/stable/usage/api/js-api.html#pyodide.setStdout
       pyodide.setStdout({ batched: (msg) => postMessage(JSON.parse(msg)) })

       console.log("Loading server.")
       await pyodide.runPythonAsync(`<<insert-your-server-init-code-here>>`)
       return pyodide
   }

Initializing the Server
^^^^^^^^^^^^^^^^^^^^^^^

Since we are not calling the server's ``start_io`` method, we need to configure the server to tell it where to write its messages.
Ideally, this would be done by calling the :meth:`~pygls.protocol.JsonRPCProtocol.set_writer` method on the server's ``protocol`` object.

However, at the time of writing there is `a bug <https://github.com/pyodide/pyodide/issues/4139>`__ in Pyodide where output is not flushed correctly, even if you call a method like ``sys.stdout.flush()``

To work around this, we will instead override one of the ``protocol`` object's methods to output the server's messages as a sequence of newline separated JSON strings.

.. code-block:: python

   # Hack to workaround https://github.com/pyodide/pyodide/issues/4139
   def send_data(data):
       body = json.dumps(data, default=server.protocol._serialize_message)
       sys.stdout.write(f"{body}\n")
       sys.stdout.flush()

   server.protocol._send_data = send_data

The above code snippet should be included along with your server's init code.

Handling Messages
^^^^^^^^^^^^^^^^^

Finally, with the server prepped to send messages, the only thing left to do is to implement the ``onmessage`` handler.

.. code-block:: typescript

   const pyodidePromise = initPyodide()

   onmessage = async (event) => {
       let pyodide = await pyodidePromise
       console.log(event.data)

       /* @ts-ignore */
       self.client_message = JSON.stringify(event.data)

       // Run Python synchronously to ensure that messages are processed in the correct order.
       pyodide.runPython(`
           from js import client_message
           message = json.loads(client_message, object_hook=server.protocol.structure_message)
           server.protocol.handle_message(message)
       `)
   }

The above handler

- Converts incoming JSON objects to a string and stores them in the ``client_message`` attribute on the WebWorker itself
- Our server code is then able to access the ``client_message`` via the ``js`` module provided by Pyodide
- The server parses and handles the given message.
