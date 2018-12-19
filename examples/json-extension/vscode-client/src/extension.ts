/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 * ----------------------------------------------------------------------- */
"use strict";

import * as net from "net";
import * as path from "path";
import { ExtensionContext, workspace } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";

let client: LanguageClient;

function isStartedInDebugMode() {
  // based on https://stackoverflow.com/a/43995223/6705061 as of 8/2/2018 9:26 AM
  const args = process.execArgv;
  if (args) {
    return args.some((arg) => /^--inspect=?/.test(arg) || /^--inspect-brk=?/.test(arg));
  }
  return false;
}

function startLangServerTCP(addr: number): LanguageClient {
  const serverOptions: ServerOptions = () => {
    return new Promise((resolve, reject) => {
      const clientSocket = new net.Socket();
      clientSocket.connect(addr, "127.0.0.1", () => {
        resolve({
          reader: clientSocket,
          writer: clientSocket,
        });
      });
    });
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: [ { scheme: "file", language: "json"} ],
    outputChannelName: "JsonLanguageServer",
    synchronize: {
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
      // In the past this told the client to actively synchronize settings. Since the
      // client now supports 'getConfiguration' requests this active synchronization is not
      // necessary anymore.
    },
  };

  return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, clientOptions);
}

function startLangServer(
  command: string, args: string[], cwd: string,
): LanguageClient {
  const serverOptions: ServerOptions = {
    args,
    command,
    options: { cwd },
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: [ { scheme: "file", language: "json"} ],
    outputChannelName: "JsonLanguageServer",
    synchronize: {
      // In the past this told the client to actively synchronize settings. Since the
      // client now supports 'getConfiguration' requests this active synchronization is not
      // necessary anymore.
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    },
  };

  return new LanguageClient(command, serverOptions, clientOptions);
}

export function activate(context: ExtensionContext) {
  if (isStartedInDebugMode()) {
    // Development - Run the server manually
    client = startLangServerTCP(2087);
  } else {
    // Production - Client is going to run the server (for use within `.vsix` package;
    // the `server` folder needs to be copied into `vscode-client/`).
    const cwd = path.join(__dirname, "../");
    const pythonPath = workspace.getConfiguration("python").get<string>("pythonPath");

    if (!pythonPath) {
      throw new Error("`python.pythonPath` is not set");
    }

    client = startLangServer(pythonPath, ["-m", "server"], cwd);
  }

  context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
