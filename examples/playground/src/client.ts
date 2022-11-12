import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';

import { MonacoLanguageClient, CloseAction, ErrorAction, MonacoServices, MessageTransports } from 'monaco-languageclient';
import { BrowserMessageReader, BrowserMessageWriter } from 'vscode-languageserver-protocol/browser.js';
import { StandaloneServices } from 'vscode/services';
import getMessageServiceOverride from 'vscode/service-override/messages';

/* @ts-ignore */
import languageServer from "./server.py";

StandaloneServices.initialize({
    ...getMessageServiceOverride(document.body)
});

// register Monaco languages
monaco.languages.register({
    id: 'plaintext',
    extensions: ['.txt'],
    aliases: ['PLAINTEXT', 'plaintext'],
    mimetypes: ['text/plain']
});

// create Monaco editor
const editorText = `
ALICE

Let's go fishing

BOB

How about next week?
`;
monaco.editor.create(document.getElementById('container')!, {
    model: monaco.editor.createModel(editorText, 'plaintext', monaco.Uri.parse('inmemory://model.txt')),
    glyphMargin: true,
    lightbulb: {
        enabled: true
    }
});

let serverModel = monaco.editor.createModel(languageServer, 'python', monaco.Uri.parse('inmemory://server.py'))
monaco.editor.create(document.getElementById('server')!, {
    model: serverModel,
    glyphMargin: true,
    lightbulb: {
        enabled: true
    }
});

function createLanguageClient (worker: Worker): MonacoLanguageClient {
    const reader = new BrowserMessageReader(worker);
    const writer = new BrowserMessageWriter(worker);

    let languageClient = new MonacoLanguageClient({
        name: 'Sample Language Client',
        clientOptions: {
            // use a language id as a document selector
            documentSelector: [{ language: 'plaintext' }],
            // disable the default error handler
            errorHandler: {
                error: () => ({ action: ErrorAction.Continue }),
                closed: () => ({ action: CloseAction.DoNotRestart })
            }
        },
        // create a language client connection to the server running in the web worker
        connectionProvider: {
            get: () => {
                return Promise.resolve({ reader, writer });
            }
        }
    });

    reader.onClose(() => {
        console.log('Reader closed! Stopping langauge client...')
        languageClient.stop()
    });

    return languageClient
}

let languageClient
let worker

async function reloadClientServer() {
    if (languageClient) {
        languageClient.stop()
    }

    if (worker) {
        worker.terminate()
    }

    worker = new Worker(new URL('./dist/serverWorker.js', window.location.href).href, { type: 'module' });
    await worker.postMessage({type: 'reload', code: serverModel.getValue()})

    languageClient = createLanguageClient(worker)
    await languageClient.start()
}


MonacoServices.install();

const reloadServerBtn = document.getElementById("serverReloadBtn")!
reloadServerBtn.addEventListener('click', async (event) => {
    await reloadClientServer()
})

reloadClientServer()
