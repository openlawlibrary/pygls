/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 * ----------------------------------------------------------------------- */
"use strict";

import * as net from "net";

import { Disposable, ExtensionContext, workspace, WorkspaceConfiguration } from "vscode";
import {
  CancellationToken, ConfigurationParams, DidChangeConfigurationNotification, LanguageClient,
  LanguageClientOptions, Middleware, ServerOptions,
} from "vscode-languageclient";

// The example settings
interface IMultiRootExampleSettings {
  maxNumberOfProblems: number;
  maxTextLength: boolean;
}

let client: LanguageClient;

function startLangServerTCP(addr: number, documentSelector: string[]): LanguageClient {
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
    documentSelector,
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
  command: string, args: string[], cwd: string, documentSelector: string[],
): LanguageClient {
  const serverOptions: ServerOptions = {
    args,
    command,
    options: { cwd },
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector,
    synchronize: {
      // In the past this told the client to actively synchronize settings. Since the
      // client now supports 'getConfiguration' requests this active synchronization is not
      // necessary anymore.
      configurationSection: ["pygls"],
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher("**/.clientrc"),
    },
  };

  return new LanguageClient(command, serverOptions, clientOptions);
}

export function activate(context: ExtensionContext) {
  // For TCP server needs to be started separately
  client = startLangServerTCP(2087, ["plaintext"]);
  context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
  if (!client) {
    return undefined;
  }
  return client.stop();
}
