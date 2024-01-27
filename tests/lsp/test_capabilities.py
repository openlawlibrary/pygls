from __future__ import annotations

import typing

import pytest
from lsprotocol import types

from pygls.lsp.capabilities import ServerCapabilitiesBuilder
from pygls.lsp.protocol import default_converter
from pygls.protocol import FeatureManager

if typing.TYPE_CHECKING:
    from typing import Any


def f():
    """A dummy function passed to feature() and command() decorators."""
    pass


def server_capabilities(**kwargs):
    """Helper to reduce the amount of boilerplate required to specify the expected
    server capabilities by filling in some fields - unless they are explicitly
    overriden."""

    if "text_document_sync" not in kwargs:
        kwargs["text_document_sync"] = types.TextDocumentSyncOptions(
            open_close=False,
            save=False,
        )

    if "execute_command_provider" not in kwargs:
        kwargs["execute_command_provider"] = types.ExecuteCommandOptions(commands=[])

    if "workspace" not in kwargs:
        kwargs["workspace"] = types.ServerCapabilitiesWorkspaceType(
            workspace_folders=types.WorkspaceFoldersServerCapabilities(
                supported=True, change_notifications=True
            ),
            file_operations=types.FileOperationOptions(),
        )

    if "position_encoding" not in kwargs:
        kwargs["position_encoding"] = types.PositionEncodingKind.Utf16

    return types.ServerCapabilities(**kwargs)


@pytest.mark.parametrize(
    "method, options, capabilities, expected",
    [
        (
            types.INITIALIZE,
            None,
            types.ClientCapabilities(
                general=types.GeneralClientCapabilities(
                    position_encodings=[types.PositionEncodingKind.Utf8]
                )
            ),
            server_capabilities(position_encoding=types.PositionEncodingKind.Utf8),
        ),
        (
            types.INITIALIZE,
            None,
            types.ClientCapabilities(
                general=types.GeneralClientCapabilities(
                    position_encodings=[
                        types.PositionEncodingKind.Utf8,
                        types.PositionEncodingKind.Utf32,
                    ]
                )
            ),
            server_capabilities(position_encoding=types.PositionEncodingKind.Utf32),
        ),
        (
            types.TEXT_DOCUMENT_DID_SAVE,
            types.SaveOptions(include_text=True),
            types.ClientCapabilities(),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=False,
                    save=types.TextDocumentSaveRegistrationOptions(include_text=True),
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_DID_SAVE,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=False, save=True
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_WILL_SAVE,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=False, save=False
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_WILL_SAVE,
            None,
            types.ClientCapabilities(
                text_document=types.TextDocumentClientCapabilities(
                    synchronization=types.TextDocumentSyncClientCapabilities(
                        will_save=True
                    )
                )
            ),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=False, save=False, will_save=True
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL,
            None,
            types.ClientCapabilities(
                text_document=types.TextDocumentClientCapabilities(
                    synchronization=types.TextDocumentSyncClientCapabilities(
                        will_save_wait_until=True
                    )
                )
            ),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=False, save=False, will_save_wait_until=True
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_DID_OPEN,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=True, save=False
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_DID_CLOSE,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                text_document_sync=types.TextDocumentSyncOptions(
                    open_close=True, save=False
                )
            ),
        ),
        (
            types.TEXT_DOCUMENT_INLAY_HINT,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                inlay_hint_provider=types.InlayHintRegistrationOptions(
                    resolve_provider=False
                ),
            ),
        ),
        (
            types.WORKSPACE_WILL_CREATE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_WILL_CREATE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        will_create=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        will_create=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_DID_CREATE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_DID_CREATE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        did_create=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        did_create=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_WILL_DELETE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_WILL_DELETE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        will_delete=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        will_delete=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_DID_DELETE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_DID_DELETE_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        did_delete=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        did_delete=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_WILL_RENAME_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_WILL_RENAME_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        will_rename=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        will_rename=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_DID_RENAME_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            types.WORKSPACE_DID_RENAME_FILES,
            types.FileOperationRegistrationOptions(
                filters=[
                    types.FileOperationFilter(
                        pattern=types.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            types.ClientCapabilities(
                workspace=types.WorkspaceClientCapabilities(
                    file_operations=types.FileOperationClientCapabilities(
                        did_rename=True
                    )
                )
            ),
            server_capabilities(
                workspace=types.ServerCapabilitiesWorkspaceType(
                    workspace_folders=types.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=types.FileOperationOptions(
                        did_rename=types.FileOperationRegistrationOptions(
                            filters=[
                                types.FileOperationFilter(
                                    pattern=types.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            types.WORKSPACE_SYMBOL,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                workspace_symbol_provider=types.WorkspaceSymbolRegistrationOptions(
                    resolve_provider=False,
                ),
            ),
        ),
        (
            types.TEXT_DOCUMENT_DIAGNOSTIC,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                diagnostic_provider=types.DiagnosticRegistrationOptions(
                    inter_file_dependencies=False,
                    workspace_diagnostics=False,
                ),
            ),
        ),
        (
            types.TEXT_DOCUMENT_DIAGNOSTIC,
            types.DiagnosticOptions(
                workspace_diagnostics=True,
                inter_file_dependencies=True,
            ),
            types.ClientCapabilities(),
            server_capabilities(
                diagnostic_provider=types.DiagnosticRegistrationOptions(
                    inter_file_dependencies=True,
                    workspace_diagnostics=False,
                ),
            ),
        ),
        (
            types.TEXT_DOCUMENT_ON_TYPE_FORMATTING,
            None,
            types.ClientCapabilities(),
            server_capabilities(
                document_on_type_formatting_provider=None,
            ),
        ),
        (
            types.TEXT_DOCUMENT_ON_TYPE_FORMATTING,
            types.DocumentOnTypeFormattingOptions(first_trigger_character=":"),
            types.ClientCapabilities(),
            server_capabilities(
                document_on_type_formatting_provider=types.DocumentOnTypeFormattingRegistrationOptions(
                    first_trigger_character=":",
                ),
            ),
        ),
    ],
)
def test_register_feature(
    method: str,
    options: Any,
    capabilities: types.ClientCapabilities,
    expected: types.ServerCapabilities,
):
    """Ensure that we can register features while specifying their associated
    options and that `pygls` is able to correctly build the corresponding server
    capabilities.

    Parameters
    ----------
    method
       The method to register the feature handler for.

    options
       The method options to use

    capabilities
       The client capabilities to use when building the server's capabilities.

    expected
       The expected server capabilties we are expecting to see.
    """

    feature_manager = FeatureManager(default_converter())
    feature_manager.feature(None, method, options)(f)

    actual = ServerCapabilitiesBuilder(
        capabilities,
        feature_manager,
        None,
        None,
    ).build()

    assert expected == actual


def test_register_inlay_hint_resolve():
    """Ensure that we compute capabilities for inlay hint resolve correctly."""
    feature_manager = FeatureManager(default_converter())
    feature_manager.feature(None, types.TEXT_DOCUMENT_INLAY_HINT)(f)
    feature_manager.feature(None, types.INLAY_HINT_RESOLVE)(f)

    expected = server_capabilities(
        inlay_hint_provider=types.InlayHintRegistrationOptions(resolve_provider=True),
    )

    actual = ServerCapabilitiesBuilder(
        types.ClientCapabilities(),
        feature_manager,
        None,
        None,
    ).build()

    assert expected == actual


def test_register_workspace_symbol_resolve():
    """Ensure that we can compute capabilities for workspace symbol resolve correctly."""
    feature_manager = FeatureManager(default_converter())
    feature_manager.feature(None, types.WORKSPACE_SYMBOL)(f)
    feature_manager.feature(None, types.WORKSPACE_SYMBOL_RESOLVE)(f)

    expected = server_capabilities(
        workspace_symbol_provider=types.WorkspaceSymbolRegistrationOptions(
            resolve_provider=True
        ),
    )

    actual = ServerCapabilitiesBuilder(
        types.ClientCapabilities(),
        feature_manager,
        None,
        None,
    ).build()

    assert expected == actual


def test_register_workspace_diagnostics():
    """Ensure that we can compute capabilities for workspace diagnostics correctly."""
    feature_manager = FeatureManager(default_converter())
    feature_manager.feature(
        None,
        types.TEXT_DOCUMENT_DIAGNOSTIC,
        identifier="example",
        inter_file_dependencies=False,
    )(f)

    feature_manager.feature(None, types.WORKSPACE_DIAGNOSTIC)(f)

    expected = server_capabilities(
        diagnostic_provider=types.DiagnosticRegistrationOptions(
            identifier="example",
            inter_file_dependencies=False,
            workspace_diagnostics=True,
        ),
    )

    actual = ServerCapabilitiesBuilder(
        types.ClientCapabilities(),
        feature_manager,
        None,
        None,
    ).build()

    assert expected == actual
