/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: // www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ----------------------------------------------------------------------- */
"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, window, workspace, WorkspaceConfiguration } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";

let client: LanguageClient;
const editor = window.activeTextEditor;

function getClientOptions(): LanguageClientOptions {
    return {
        // Register the server for plain text documents
        documentSelector: [
            { scheme: "file", language: "json" },
            { scheme: "untitled", language: "json" },
        ],
        outputChannelName: "[pygls] JsonLanguageServer",
        synchronize: {
            // Notify the server about file changes to '.clientrc files contain in the workspace
            fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
        },
    };
}

function isStartedInDebugMode(): boolean {
    return process.env.VSCODE_DEBUG_MODE === "true";
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

function getConfig(key: string): WorkspaceConfiguration {
    return workspace.getConfiguration(key, editor ? editor.document.uri : null);
}

function getPython(): string {
    return getConfig("python").get<string>("pythonPath");
}

export function activate(context: ExtensionContext) {
    const debugPort = process.env.DebugTCP;
    const config = getConfig("jsonServer");
    if (debugPort) {
        // Debug port: server should be running externally on specified port.
        client = startLangServerTCP(Number(debugPort));
    } else {
        // No debug port: run server executable.
        const cwd = path.join(__dirname, "../");

        let serverPath = config.get<string>("serverPath");
        let serverArgs = config.get<string[]>("serverArgs");
        if (!serverPath) {
            serverPath = getPython() || "python";
            serverArgs = ["-m", "server"];
        }
        client = startLangServer(serverPath, serverArgs, cwd);
    }

    context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
