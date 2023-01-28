import { ExtensionContext, Uri } from "vscode";
import { LanguageClientOptions } from "vscode-languageclient";
import { LanguageClient } from "vscode-languageclient/browser";

export function activate(context: ExtensionContext) {
    console.log("extension activated")

    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'vscode-vfs', language: 'fountain' }
        ],
        outputChannelName: "Fountain Language Server"
    }

    const path = Uri.joinPath(context.extensionUri, "out/server.js")
    const worker = new Worker(path.toString())

    const client = new LanguageClient("fountain-extension", "Fountain Extension", clientOptions, worker)
    context.subscriptions.push(client.start())

    client.onReady().then(() => {
        console.log("fountain-extension server is ready")
    })
}