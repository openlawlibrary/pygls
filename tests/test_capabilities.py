from typing import Set

import pytest
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_WILL_SAVE,
    TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL,
    ClientCapabilities,
    SaveOptions,
    TextDocumentClientCapabilities,
    TextDocumentSaveRegistrationOptions,
    TextDocumentSyncClientCapabilities,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
)

from pygls.capabilities import ServerCapabilitiesBuilder


@pytest.mark.parametrize("capabilities,features,options,expected", [

    # textDocument/didOpen
    (
        ClientCapabilities(),
        set(),
        {},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=False,
        )
    ),
    (
        ClientCapabilities(),
        {TEXT_DOCUMENT_DID_OPEN},
        {},
        TextDocumentSyncOptions(
            open_close=True,
            change=TextDocumentSyncKind.Incremental,
            save=False,
        )
    ),
    (
        ClientCapabilities(),
        {TEXT_DOCUMENT_DID_CLOSE},
        {},
        TextDocumentSyncOptions(
            open_close=True,
            change=TextDocumentSyncKind.Incremental,
            save=False,
        )
    ),
    # textDocument/willSave & textDocument/willSaveWaitUntil
    (
        ClientCapabilities(),
        {TEXT_DOCUMENT_WILL_SAVE},
        {},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=False,
        )
    ),
    (
        ClientCapabilities(
            text_document=TextDocumentClientCapabilities(
                synchronization=TextDocumentSyncClientCapabilities(
                    will_save=True
                )
            )
        ),
        {TEXT_DOCUMENT_WILL_SAVE},
        {},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=False,
            will_save=True
        )
    ),
    (
        ClientCapabilities(
            text_document=TextDocumentClientCapabilities(
                synchronization=TextDocumentSyncClientCapabilities(
                    will_save_wait_until=True
                )
            )
        ),
        {TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL},
        {},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=False,
            will_save_wait_until=True
        )
    ),
    # textDocument/didSave
    (
        ClientCapabilities(),
        {TEXT_DOCUMENT_DID_SAVE},
        {},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=True,
        )
    ),
    (
        ClientCapabilities(),
        {TEXT_DOCUMENT_DID_SAVE},
        {TEXT_DOCUMENT_DID_SAVE: TextDocumentSaveRegistrationOptions(include_text=True)},
        TextDocumentSyncOptions(
            open_close=False,
            change=TextDocumentSyncKind.Incremental,
            save=SaveOptions(include_text=True),
        )
    )
])
def test_text_doc_sync_capabilities(
    capabilities: ClientCapabilities,
    features: Set[str],
    options,
    expected: TextDocumentSyncOptions
):
    """Ensure that `pygls` can correctly construct server capabilities for the
    text document sync features."""

    builder = ServerCapabilitiesBuilder(
        capabilities, features, options, [], TextDocumentSyncKind.Incremental
    )

    actual = builder.build().text_document_sync
    assert expected == actual
