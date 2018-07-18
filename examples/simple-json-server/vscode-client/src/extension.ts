/* -------------------------------------------------------------------------
 * Original work Copyright (c) Microsoft Corporation. All rights reserved.
 * Original work licensed under the MIT License.
 * See ThirdPartyNotices.txt in the project root for license information.
 * All modifications Copyright (c) Open Law Library. All rights reserved.
 * ----------------------------------------------------------------------- */
"use strict";

import * as net from "net";

import { ExtensionContext } from "vscode";
import { LanguageClient, LanguageClientOptions, ServerOptions } from "vscode-languageclient";

export function activate(context: ExtensionContext) {

  const extensionName = "[JSON-PYGLS]";

  const serverOptions: ServerOptions = () => {
    return new Promise((resolve, reject) => {
      const clientSocket = new net.Socket();
      clientSocket.connect(2087, "127.0.0.1", () => {
        resolve({
          reader: clientSocket,
          writer: clientSocket,
        });
      });
    });
  };

  const clientOptions: LanguageClientOptions = {
    documentSelector: ["json"],
    outputChannelName: extensionName,
  };

  const client = new LanguageClient(extensionName, serverOptions, clientOptions);

  context.subscriptions.push(client.start());
}
