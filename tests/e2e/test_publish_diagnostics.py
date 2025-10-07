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
from __future__ import annotations

import asyncio
import typing

import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture()
async def push_diagnostics(get_client_for):
    async for client, response in get_client_for("publish_diagnostics.py"):
        # Setup a diagnostics handler
        client.diagnostics = {}

        @client.feature(types.TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
        def publish_diagnostics(params: types.PublishDiagnosticsParams):
            client.diagnostics[params.uri] = params.diagnostics

        yield client, response


async def test_publish_diagnostics(
    push_diagnostics: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
):
    """Ensure that the publish diagnostics server is working as expected."""
    client, initialize_result = push_diagnostics

    test_uri = uri_for("sums.txt")
    test_path = path_for("sums.txt")

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            types.TextDocumentItem(
                uri=test_uri,
                language_id="plaintext",
                version=0,
                text=test_path.read_text(),
            )
        )
    )

    await asyncio.sleep(0.5)
    assert test_uri in client.diagnostics

    expected = (
        types.Diagnostic(
            message="Missing answer",
            severity=types.DiagnosticSeverity.Warning,
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=0, character=7),
            ),
        ),
        types.Diagnostic(
            message="Missing answer",
            severity=types.DiagnosticSeverity.Warning,
            range=types.Range(
                start=types.Position(line=3, character=0),
                end=types.Position(line=3, character=7),
            ),
        ),
        types.Diagnostic(
            message="Missing answer",
            severity=types.DiagnosticSeverity.Warning,
            range=types.Range(
                start=types.Position(line=6, character=0),
                end=types.Position(line=6, character=7),
            ),
        ),
    )

    assert expected == tuple(client.diagnostics[test_uri])

    # Write an incorrect answer...
    client.text_document_did_change(
        types.DidChangeTextDocumentParams(
            text_document=types.VersionedTextDocumentIdentifier(
                uri=test_uri, version=1
            ),
            content_changes=[
                types.TextDocumentContentChangePartial(
                    text=" 12",
                    range=types.Range(
                        start=types.Position(line=0, character=7),
                        end=types.Position(line=0, character=7),
                    ),
                )
            ],
        )
    )

    await asyncio.sleep(0.5)
    assert test_uri in client.diagnostics

    expected = (
        types.Diagnostic(
            message="Incorrect answer: 12",
            severity=types.DiagnosticSeverity.Error,
            range=types.Range(
                start=types.Position(line=0, character=0),
                end=types.Position(line=0, character=10),
            ),
        ),
        types.Diagnostic(
            message="Missing answer",
            severity=types.DiagnosticSeverity.Warning,
            range=types.Range(
                start=types.Position(line=3, character=0),
                end=types.Position(line=3, character=7),
            ),
        ),
        types.Diagnostic(
            message="Missing answer",
            severity=types.DiagnosticSeverity.Warning,
            range=types.Range(
                start=types.Position(line=6, character=0),
                end=types.Position(line=6, character=7),
            ),
        ),
    )

    assert expected == tuple(client.diagnostics[test_uri])
