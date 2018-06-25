/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */
'use strict';

import * as net from 'net';


import { ExtensionContext } from 'vscode';
import {
  LanguageClient, LanguageClientOptions, ServerOptions
} from 'vscode-languageclient';


export function activate(context: ExtensionContext) {

  const extensionName = '[JSON-PYGLS]';

  const serverOptions: ServerOptions = function () {
    return new Promise((resolve, reject) => {
      var client = new net.Socket();
      client.connect(2087, "127.0.0.1", function () {
        resolve({
          reader: client,
          writer: client
        });
      });
    });
  }

  const clientOptions: LanguageClientOptions = {
    documentSelector: ['json'],
    outputChannelName: extensionName
  }

  let client = new LanguageClient(extensionName, serverOptions, clientOptions);

  context.subscriptions.push(client.start());
}
