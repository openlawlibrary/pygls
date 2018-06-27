/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 * ----------------------------------------------------------------------- */
'use strict';

import * as net from 'net';


import { workspace, ExtensionContext, WorkspaceConfiguration, Disposable } from 'vscode';
import {
  LanguageClient, LanguageClientOptions, ServerOptions, CancellationToken, Middleware,
  DidChangeConfigurationNotification, ConfigurationParams
} from 'vscode-languageclient';

// The example settings
interface MultiRootExampleSettings {
  maxNumberOfProblems: number;
  maxTextLength: boolean;
}

let client: LanguageClient;

namespace Configuration {

  let configurationListener: Disposable;

  // Convert VS Code specific settings to a format acceptable by the server. Since
  // both client and server do use JSON the conversion is trivial.
  export function computeConfiguration(params: ConfigurationParams, _token: CancellationToken, _next: Function): any[] {
    if (!params.items) {
      return null;
    }
    let result: (MultiRootExampleSettings | null)[] = [];
    for (let item of params.items) {
      // The server asks the client for configuration settings without a section
      // If a section is present we return null to indicate that the configuration
      // is not supported.
      if (item.section) {
        result.push(null);
        continue;
      }
      let config: WorkspaceConfiguration;
      if (item.scopeUri) {
        config = workspace.getConfiguration('pygls', client.protocol2CodeConverter.asUri(item.scopeUri));
      } else {
        config = workspace.getConfiguration('pygls');
      }
      result.push({
        maxNumberOfProblems: config.get('maxNumberOfProblems'),
        maxTextLength: config.get('maxTextLength')
      });
    }
    return result;
  }

  export function initialize() {
    // VS Code currently doesn't sent fine grained configuration changes. So we
    // listen to any change. However this will change in the near future.
    configurationListener = workspace.onDidChangeConfiguration(() => {
      const type = DidChangeConfigurationNotification.type
      client.sendNotification(type, { settings: null });
    });
  }

  export function dispose() {
    if (configurationListener) {
      configurationListener.dispose();
    }
  }
}

function startLangServerTCP(addr: number, documentSelector: string[]): LanguageClient {
  const serverOptions: ServerOptions = function () {
    return new Promise((resolve, reject) => {
      var client = new net.Socket();
      client.connect(addr, "127.0.0.1", function () {
        resolve({
          reader: client,
          writer: client
        });
      });
    });
  }

  let middleware: Middleware = {
    workspace: {
      configuration: Configuration.computeConfiguration
    }
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: documentSelector,
    synchronize: {
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher('**/.clientrc'),
      // In the past this told the client to actively synchronize settings. Since the
      // client now supports 'getConfiguration' requests this active synchronization is not
      // necessary anymore.
      configurationSection: ['pygls']
    },
    middleware: middleware
  }

  return new LanguageClient(`tcp lang server (port ${addr})`, serverOptions, clientOptions);
}

function startLangServer(command: string, args: string[], cwd: string, documentSelector: string[]): LanguageClient {
  const serverOptions: ServerOptions = {
    command,
    args,
    options: {
      cwd: cwd
    }
  };

  let middleware: Middleware = {
    workspace: {
      configuration: Configuration.computeConfiguration
    }
  };

  // Options to control the language client
  const clientOptions: LanguageClientOptions = {
    // Register the server for plain text documents
    documentSelector: documentSelector,
    synchronize: {
      // Notify the server about file changes to '.clientrc files contain in the workspace
      fileEvents: workspace.createFileSystemWatcher('**/.clientrc'),
      // In the past this told the client to actively synchronize settings. Since the
      // client now supports 'getConfiguration' requests this active synchronization is not
      // necessary anymore.
      configurationSection: ['pygls']
    },
    middleware: middleware
  }

  return new LanguageClient(command, serverOptions, clientOptions);
}


export function activate(context: ExtensionContext) {
  // let python = "C:\\Users\\Daniel Elero\\Envs\\pygls\\Scripts\\python.exe";

  // client = startLangServer(python, ["-m", "pygls"], "C:\\code\\openlawlibrary\\pygls", ["plaintext"]);
  // context.subscriptions.push(client.start());
  // For TCP server needs to be started separately

  client = startLangServerTCP(2087, ["plaintext"])
  context.subscriptions.push(client.start());
}

export function deactivate(): Thenable<void> {
  if (!client) {
    return undefined;
  }
  Configuration.dispose();
  return client.stop();
}
