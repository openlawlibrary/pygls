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

import typing

import pytest_asyncio
from lsprotocol import types

if typing.TYPE_CHECKING:
    from typing import Tuple

    from pygls.lsp.client import BaseLanguageClient


@pytest_asyncio.fixture()
async def pull_diagnostics(get_client_for):
    async for result in get_client_for("pull_diagnostics.py"):
        yield result


async def test_document_diagnostics(
    pull_diagnostics: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
):
    """Ensure that the pull diagnostics server is working as expected."""
    client, initialize_result = pull_diagnostics

    diagnostic_options = initialize_result.capabilities.diagnostic_provider
    assert diagnostic_options.identifier == "pull-diagnostics"
    assert diagnostic_options.workspace_diagnostics is True

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

    result = await client.text_document_diagnostic_async(
        types.DocumentDiagnosticParams(
            text_document=types.TextDocumentIdentifier(test_uri)
        )
    )

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

    assert result.result_id == f"{test_uri}@{0}"
    assert tuple(result.items) == expected
    assert result.kind == types.DocumentDiagnosticReportKind.Full

    # Write a correct answer...
    client.text_document_did_change(
        types.DidChangeTextDocumentParams(
            text_document=types.VersionedTextDocumentIdentifier(
                uri=test_uri, version=1
            ),
            content_changes=[
                types.TextDocumentContentChangePartial(
                    text=" 2",
                    range=types.Range(
                        start=types.Position(line=0, character=7),
                        end=types.Position(line=0, character=7),
                    ),
                )
            ],
        )
    )

    result = await client.text_document_diagnostic_async(
        types.DocumentDiagnosticParams(
            text_document=types.TextDocumentIdentifier(test_uri)
        )
    )

    expected = (
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

    assert result.result_id == f"{test_uri}@{1}"
    assert tuple(result.items) == expected
    assert result.kind == types.DocumentDiagnosticReportKind.Full


async def test_document_diagnostic_unchanged(
    pull_diagnostics: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
):
    """Ensure that the pull diagnostics server is working as expected."""
    client, initialize_result = pull_diagnostics

    diagnostic_options = initialize_result.capabilities.diagnostic_provider
    assert diagnostic_options.identifier == "pull-diagnostics"
    assert diagnostic_options.workspace_diagnostics is True

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

    result = await client.text_document_diagnostic_async(
        types.DocumentDiagnosticParams(
            text_document=types.TextDocumentIdentifier(test_uri)
        )
    )

    expected_id = f"{test_uri}@{0}"

    assert result.result_id == expected_id
    assert len(result.items) > 0
    assert result.kind == types.DocumentDiagnosticReportKind.Full

    # Making second request should result in an unchanged response
    result = await client.text_document_diagnostic_async(
        types.DocumentDiagnosticParams(
            text_document=types.TextDocumentIdentifier(test_uri),
            previous_result_id=expected_id,
        )
    )

    assert result.result_id == expected_id
    assert result.kind == types.DocumentDiagnosticReportKind.Unchanged


async def test_workspace_diagnostic(
    pull_diagnostics: Tuple[BaseLanguageClient, types.InitializeResult],
    path_for,
    uri_for,
):
    """Ensure that the pull diagnostics server is working as expected."""
    client, initialize_result = pull_diagnostics

    diagnostic_options = initialize_result.capabilities.diagnostic_provider
    assert diagnostic_options.identifier == "pull-diagnostics"
    assert diagnostic_options.workspace_diagnostics is True

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

    result = await client.workspace_diagnostic_async(
        types.WorkspaceDiagnosticParams(previous_result_ids=[])
    )

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

    report = result.items[0]
    assert report.uri == test_uri
    assert report.version == 0
    assert tuple(report.items) == expected
    assert report.kind == types.DocumentDiagnosticReportKind.Full

    result = await client.workspace_diagnostic_async(
        types.WorkspaceDiagnosticParams(
            previous_result_ids=[
                types.PreviousResultId(uri=test_uri, value=f"{test_uri}@{0}")
            ]
        )
    )

    report = result.items[0]
    assert report.uri == test_uri
    assert report.version == 0
    assert report.kind == types.DocumentDiagnosticReportKind.Unchanged
