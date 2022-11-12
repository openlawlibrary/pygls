from typing import Set

import pytest
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_WILL_SAVE,
    TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL,
    WORKSPACE_DID_CREATE_FILES,
    WORKSPACE_WILL_CREATE_FILES,
    WORKSPACE_DID_DELETE_FILES,
    WORKSPACE_WILL_DELETE_FILES,
    WORKSPACE_DID_RENAME_FILES,
    WORKSPACE_WILL_RENAME_FILES,
    ClientCapabilities,
    FileOperationClientCapabilities,
    FileOperationFilter,
    FileOperationOptions,
    FileOperationPattern,
    FileOperationRegistrationOptions,
    SaveOptions,
    TextDocumentClientCapabilities,
    TextDocumentSaveRegistrationOptions,
    TextDocumentSyncClientCapabilities,
    TextDocumentSyncKind,
    TextDocumentSyncOptions,
    WorkspaceClientCapabilities,
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


@pytest.mark.parametrize("capabilities,features,options,expected", [
    (
        ClientCapabilities(),
        set(),
        {},
        FileOperationOptions()
    ),
    # workspace/willCreateFiles
    (
        ClientCapabilities(),
        {WORKSPACE_WILL_CREATE_FILES},
        {
            WORKSPACE_WILL_CREATE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    will_create=True
                )
            )
        ),
        {WORKSPACE_WILL_CREATE_FILES},
        {
            WORKSPACE_WILL_CREATE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            will_create=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
    # workspace/didCreateFiles
    (
        ClientCapabilities(),
        {WORKSPACE_DID_CREATE_FILES},
        {
            WORKSPACE_DID_CREATE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    did_create=True
                )
            )
        ),
        {WORKSPACE_DID_CREATE_FILES},
        {
            WORKSPACE_DID_CREATE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            did_create=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
    # workspace/willDeleteFiles
    (
        ClientCapabilities(),
        {WORKSPACE_WILL_DELETE_FILES},
        {
            WORKSPACE_WILL_DELETE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    will_delete=True
                )
            )
        ),
        {WORKSPACE_WILL_DELETE_FILES},
        {
            WORKSPACE_WILL_DELETE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            will_delete=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
    # workspace/didDeleteFiles
    (
        ClientCapabilities(),
        {WORKSPACE_DID_DELETE_FILES},
        {
            WORKSPACE_DID_DELETE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    did_delete=True
                )
            )
        ),
        {WORKSPACE_DID_DELETE_FILES},
        {
            WORKSPACE_DID_DELETE_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            did_delete=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
    # workspace/willRenameFiles
    (
        ClientCapabilities(),
        {WORKSPACE_WILL_RENAME_FILES},
        {
            WORKSPACE_WILL_RENAME_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    will_rename=True
                )
            )
        ),
        {WORKSPACE_WILL_RENAME_FILES},
        {
            WORKSPACE_WILL_RENAME_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            will_rename=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
    # workspace/didRenameFiles
    (
        ClientCapabilities(),
        {WORKSPACE_DID_RENAME_FILES},
        {
            WORKSPACE_DID_RENAME_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions()
    ),
    (
        ClientCapabilities(
            workspace=WorkspaceClientCapabilities(
                file_operations=FileOperationClientCapabilities(
                    did_rename=True
                )
            )
        ),
        {WORKSPACE_DID_RENAME_FILES},
        {
            WORKSPACE_DID_RENAME_FILES: FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        },
        FileOperationOptions(
            did_rename=FileOperationRegistrationOptions(
                filters=[
                    FileOperationFilter(
                        pattern=FileOperationPattern(glob="**/*.py")
                    )
                ]
            )
        )
    ),
])
def test_file_operations_capabilities(
    capabilities: ClientCapabilities,
    features: Set[str],
    options,
    expected: FileOperationOptions
):
    """Ensure that `pygls` can correctly construct server capabilities for the file
    operations set of features."""

    builder = ServerCapabilitiesBuilder(
        capabilities, features, options, [], TextDocumentSyncKind.Incremental
    )

    server = builder.build()
    assert server.workspace is not None

    actual = server.workspace.file_operations
    assert expected == actual
