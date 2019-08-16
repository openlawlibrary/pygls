"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";

let client: LanguageClient;

function getClientOptions(): LanguageClientOptions {
    return {
        // Register the server for plain text documents
        documentSelector: [
            { scheme: "file", language: "json" },
            { scheme: "untitled", language: "json" },
        ],
        outputChannelName: "JSON Language Server",
        synchronize: {
            // Notify the server about file changes to '.clientrc files contain in the workspace
            fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
        },
    };
}

function startLangServerTCP(port: number): LanguageClient {
    const serverOptions: ServerOptions = () => {
        return new Promise((resolve, reject) => {
            const clientSocket = new net.Socket();
            clientSocket.connect(port, "127.0.0.1", () => {
                resolve({
                    reader: clientSocket,
                    writer: clientSocket,
                });
            });
        });
    };

    return new LanguageClient(`tcp lang server (port ${port})`, serverOptions, getClientOptions());
}

function startLangServer(
    command: string, args: string[], cwd: string,
): LanguageClient {
    const serverOptions: ServerOptions = {
        args,
        command,
        options: { cwd },
    };

    return new LanguageClient(command, serverOptions, getClientOptions());
}


export function activate(context: ExtensionContext) {
    let tcpPort = process.env.DebugTCP
    if (!tcpPort) {
        // No debug port: run server executable from (set) path.
        const cwd = path.join(__dirname, "../");
        let serverPath = workspace.getConfiguration("jsonServer").get<string>("serverPath");
        if (!serverPath) {
            serverPath = "json_server"; // Let it up to the user to put it on PATH.
        }
        client = startLangServer(serverPath, [], cwd);
    } else {
        // Debug port: server is running externally on specified port.
        client = startLangServerTCP(parseInt(tcpPort))
    }

    context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
    if (!client) {
        return undefined;
    }
    return client.stop()
}