############################################################################
# Copyright(c) Open Law Library. All rights reserved.                      #
# See ThirdPartyNotices.txt in the project root for additional notices.    #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License")           #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http: // www.apache.org/licenses/LICENSE-2.0                         #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################
"""This implements the push-model of diagnostics.

This is a fairly new addition to LSP (v3.17), so not all clients will support this.

Instead of the server broadcasting updates whenever it feels like, the client explicitly
requests diagnostics for a particular document (:lsp:`textDocument/diagnostic`) or for
the entire workspace (:lsp:`workspace/diagnostic`).
This approach helps guide the server to perform work that's most relevant to the client.

This server scans a document for sums e.g. ``1 + 2 = 3``, highlighting any that are
either missing answers (warnings) or incorrect (errors).
"""

import logging
import re

from lsprotocol import types

from pygls.cli import start_server
from pygls.lsp.server import LanguageServer
from pygls.workspace import TextDocument

ADDITION = re.compile(r"^\s*(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)?$")


class PullDiagnosticServer(LanguageServer):
    """Language server demonstrating "pull-model" diagnostics."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.diagnostics = {}

    def parse(self, document: TextDocument):
        _, previous = self.diagnostics.get(document.uri, (0, []))
        diagnostics = []

        for idx, line in enumerate(document.lines):
            match = ADDITION.match(line)
            if match is not None:
                left = int(match.group(1))
                right = int(match.group(2))

                expected_answer = left + right
                actual_answer = match.group(3)

                if actual_answer is not None and expected_answer == int(actual_answer):
                    continue

                if actual_answer is None:
                    message = "Missing answer"
                    severity = types.DiagnosticSeverity.Warning
                else:
                    message = f"Incorrect answer: {actual_answer}"
                    severity = types.DiagnosticSeverity.Error

                diagnostics.append(
                    types.Diagnostic(
                        message=message,
                        severity=severity,
                        range=types.Range(
                            start=types.Position(line=idx, character=0),
                            end=types.Position(line=idx, character=len(line) - 1),
                        ),
                    )
                )

        # Only update if the list has changed
        if previous != diagnostics:
            self.diagnostics[document.uri] = (document.version, diagnostics)

        # logging.info("%s", self.diagnostics)


server = PullDiagnosticServer("diagnostic-server", "v1")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: PullDiagnosticServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is opened"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: PullDiagnosticServer, params: types.DidOpenTextDocumentParams):
    """Parse each document when it is changed"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(
    types.TEXT_DOCUMENT_DIAGNOSTIC,
    types.DiagnosticOptions(
        identifier="pull-diagnostics",
        inter_file_dependencies=False,
        workspace_diagnostics=True,
    ),
)
def document_diagnostic(
    ls: PullDiagnosticServer, params: types.DocumentDiagnosticParams
):
    """Return diagnostics for the requested document"""
    # logging.info("%s", params)

    if (uri := params.text_document.uri) not in ls.diagnostics:
        return

    version, diagnostics = ls.diagnostics[uri]
    result_id = f"{uri}@{version}"

    if result_id == params.previous_result_id:
        return types.UnchangedDocumentDiagnosticReport(result_id)

    return types.FullDocumentDiagnosticReport(items=diagnostics, result_id=result_id)


@server.feature(types.WORKSPACE_DIAGNOSTIC)
def workspace_diagnostic(
    ls: PullDiagnosticServer, params: types.WorkspaceDiagnosticParams
):
    """Return diagnostics for the workspace."""
    # logging.info("%s", params)
    items = []
    previous_ids = {result.value for result in params.previous_result_ids}

    for uri, (version, diagnostics) in ls.diagnostics.items():
        result_id = f"{uri}@{version}"
        if result_id in previous_ids:
            items.append(
                types.WorkspaceUnchangedDocumentDiagnosticReport(
                    uri=uri, result_id=result_id, version=version
                )
            )
        else:
            items.append(
                types.WorkspaceFullDocumentDiagnosticReport(
                    uri=uri,
                    version=version,
                    items=diagnostics,
                )
            )

    return types.WorkspaceDiagnosticReport(items=items)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    start_server(server)
