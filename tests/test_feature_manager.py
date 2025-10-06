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
import asyncio
from typing import Any

import pytest
from lsprotocol import types as lsp

from pygls.capabilities import ServerCapabilitiesBuilder
from pygls.exceptions import (
    CommandAlreadyRegisteredError,
    FeatureAlreadyRegisteredError,
    ValidationError,
)
from pygls.feature_manager import (
    FeatureManager,
    has_ls_param_or_annotation,
    wrap_with_server,
)
from pygls.lsp.client import BaseLanguageClient, LanguageClient
from pygls.lsp.server import BaseLanguageServer, LanguageServer


def f1(ls, a, b, c): ...
def f2(server: LanguageServer, a, b, c): ...
def f3(server: "LanguageServer", a, b, c): ...
def f4(server: BaseLanguageServer, a, b, c): ...
def f5(server: "BaseLanguageServer", a, b, c): ...
def f6(client: LanguageClient, a, b, c): ...
def f7(client: "LanguageClient", a, b, c): ...
def f8(client: BaseLanguageClient, a, b, c): ...
def f9(client: "BaseLanguageClient", a, b, c): ...


@pytest.mark.parametrize(
    "fn,cls,result",
    [
        (f1, None, True),
        (f2, LanguageServer, True),
        (f2, BaseLanguageServer, False),
        (f3, LanguageServer, True),
        (f3, BaseLanguageServer, False),
        (f4, BaseLanguageServer, True),
        (f4, LanguageServer, True),
        (f5, BaseLanguageServer, True),
        (f5, LanguageServer, True),
        (f6, LanguageClient, True),
        (f6, BaseLanguageClient, False),
        (f7, LanguageClient, True),
        (f7, BaseLanguageClient, False),
        (f8, BaseLanguageClient, True),
        (f8, LanguageClient, True),
        (f9, BaseLanguageClient, True),
        (f9, LanguageClient, True),
    ],
)
def test_has_ls_param_or_annotation(fn, cls, result: bool):
    """Ensure that the ``has_ls_param_or_annotation`` works as expected"""
    assert has_ls_param_or_annotation(fn, cls) == result


def test_register_command_validation_error(feature_manager):
    with pytest.raises(ValidationError):

        @feature_manager.command(" \n\t")
        def cmd1():  # pylint: disable=unused-variable
            pass


def test_register_commands(feature_manager):
    cmd1_name = "cmd1"
    cmd2_name = "cmd2"

    @feature_manager.command(cmd1_name)
    def cmd1():
        pass

    @feature_manager.command(cmd2_name)
    def cmd2():
        pass

    reg_commands = feature_manager.commands.keys()

    assert cmd1_name in reg_commands
    assert cmd2_name in reg_commands

    assert feature_manager.commands[cmd1_name] is cmd1
    assert feature_manager.commands[cmd2_name] is cmd2


def test_register_feature_with_valid_options(feature_manager):
    options = lsp.CompletionOptions(trigger_characters=["!"])

    @feature_manager.feature(lsp.TEXT_DOCUMENT_COMPLETION, options)
    def completions():
        pass

    reg_features = feature_manager.features.keys()
    reg_feature_options = feature_manager.feature_options.keys()

    assert lsp.TEXT_DOCUMENT_COMPLETION in reg_features
    assert lsp.TEXT_DOCUMENT_COMPLETION in reg_feature_options

    assert feature_manager.features[lsp.TEXT_DOCUMENT_COMPLETION] is completions
    assert feature_manager.feature_options[lsp.TEXT_DOCUMENT_COMPLETION] is options


def test_register_feature_with_wrong_options(feature_manager):
    class Options:
        pass

    with pytest.raises(
        AttributeError,
        match=("'Options' object has no attribute 'trigger_characters'"),  # noqa
    ):

        @feature_manager.feature(lsp.TEXT_DOCUMENT_COMPLETION, Options())
        def completions():
            pass


def test_register_features(feature_manager):
    @feature_manager.feature(lsp.TEXT_DOCUMENT_COMPLETION)
    def completions():
        pass

    @feature_manager.feature(lsp.TEXT_DOCUMENT_CODE_LENS)
    def code_lens():
        pass

    reg_features = feature_manager.features.keys()

    assert lsp.TEXT_DOCUMENT_COMPLETION in reg_features
    assert lsp.TEXT_DOCUMENT_CODE_LENS in reg_features

    assert feature_manager.features[lsp.TEXT_DOCUMENT_COMPLETION] is completions
    assert feature_manager.features[lsp.TEXT_DOCUMENT_CODE_LENS] is code_lens


def test_register_same_command_twice_error(feature_manager):
    with pytest.raises(CommandAlreadyRegisteredError):

        @feature_manager.command("cmd1")
        def cmd1():  # pylint: disable=unused-variable
            pass

        @feature_manager.command("cmd1")
        def cmd2():  # pylint: disable=unused-variable
            pass


def test_register_same_feature_twice_error(feature_manager):
    with pytest.raises(FeatureAlreadyRegisteredError):

        @feature_manager.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
        def code_action1():  # pylint: disable=unused-variable
            pass

        @feature_manager.feature(lsp.TEXT_DOCUMENT_CODE_ACTION)
        def code_action2():  # pylint: disable=unused-variable
            pass


def test_wrap_with_server_async():
    class Server:
        pass

    async def f(ls):
        assert isinstance(ls, Server)

    wrapped = wrap_with_server(f, Server())
    assert asyncio.iscoroutinefunction(wrapped)


def test_wrap_with_server_sync():
    class Server:
        pass

    def f(ls):
        assert isinstance(ls, Server)

    wrapped = wrap_with_server(f, Server())
    wrapped()


def test_wrap_with_server_thread():
    class Server:
        pass

    def f(ls):
        assert isinstance(ls, Server)

    f.execute_in_thread = True

    wrapped = wrap_with_server(f, Server())
    assert wrapped.execute_in_thread is True


def server_capabilities(**kwargs):
    """Helper to reduce the amount of boilerplate required to specify the expected
    server capabilities by filling in some fields - unless they are explicitly
    overriden."""

    if "text_document_sync" not in kwargs:
        kwargs["text_document_sync"] = lsp.TextDocumentSyncOptions(
            open_close=False,
            save=False,
        )

    if "execute_command_provider" not in kwargs:
        kwargs["execute_command_provider"] = lsp.ExecuteCommandOptions(commands=[])

    if "workspace" not in kwargs:
        kwargs["workspace"] = lsp.WorkspaceOptions(
            workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                supported=True, change_notifications=True
            ),
            file_operations=lsp.FileOperationOptions(),
        )

    if "position_encoding" not in kwargs:
        kwargs["position_encoding"] = lsp.PositionEncodingKind.Utf16

    return lsp.ServerCapabilities(**kwargs)


@pytest.mark.parametrize(
    "method, options, capabilities, expected",
    [
        (
            lsp.INITIALIZE,
            None,
            lsp.ClientCapabilities(
                general=lsp.GeneralClientCapabilities(
                    position_encodings=[lsp.PositionEncodingKind.Utf8]
                )
            ),
            server_capabilities(position_encoding=lsp.PositionEncodingKind.Utf8),
        ),
        (
            lsp.INITIALIZE,
            None,
            lsp.ClientCapabilities(
                general=lsp.GeneralClientCapabilities(
                    position_encodings=[
                        lsp.PositionEncodingKind.Utf8,
                        lsp.PositionEncodingKind.Utf32,
                    ]
                )
            ),
            server_capabilities(position_encoding=lsp.PositionEncodingKind.Utf8),
        ),
        (
            lsp.INITIALIZE,
            None,
            lsp.ClientCapabilities(
                general=lsp.GeneralClientCapabilities(
                    position_encodings=[
                        lsp.PositionEncodingKind.Utf32,
                        lsp.PositionEncodingKind.Utf8,
                    ]
                )
            ),
            server_capabilities(position_encoding=lsp.PositionEncodingKind.Utf32),
        ),
        (
            lsp.TEXT_DOCUMENT_DID_SAVE,
            lsp.SaveOptions(include_text=True),
            lsp.ClientCapabilities(),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=False, save=lsp.SaveOptions(include_text=True)
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_DID_SAVE,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=False, save=True
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_WILL_SAVE,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=False, save=False
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_WILL_SAVE,
            None,
            lsp.ClientCapabilities(
                text_document=lsp.TextDocumentClientCapabilities(
                    synchronization=lsp.TextDocumentSyncClientCapabilities(
                        will_save=True
                    )
                )
            ),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=False, save=False, will_save=True
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_WILL_SAVE_WAIT_UNTIL,
            None,
            lsp.ClientCapabilities(
                text_document=lsp.TextDocumentClientCapabilities(
                    synchronization=lsp.TextDocumentSyncClientCapabilities(
                        will_save_wait_until=True
                    )
                )
            ),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=False, save=False, will_save_wait_until=True
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_DID_OPEN,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=True, save=False
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_DID_CLOSE,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                text_document_sync=lsp.TextDocumentSyncOptions(
                    open_close=True, save=False
                )
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_INLAY_HINT,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                inlay_hint_provider=lsp.InlayHintOptions(resolve_provider=False),
            ),
        ),
        (
            lsp.WORKSPACE_WILL_CREATE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_WILL_CREATE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(
                        will_create=True
                    )
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        will_create=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_DID_CREATE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_DID_CREATE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(did_create=True)
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        did_create=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_WILL_DELETE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_WILL_DELETE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(
                        will_delete=True
                    )
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        will_delete=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_DID_DELETE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_DID_DELETE_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(did_delete=True)
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        did_delete=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_WILL_RENAME_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_WILL_RENAME_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(
                        will_rename=True
                    )
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        will_rename=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_DID_RENAME_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(),
            server_capabilities(),
        ),
        (
            lsp.WORKSPACE_DID_RENAME_FILES,
            lsp.FileOperationRegistrationOptions(
                filters=[
                    lsp.FileOperationFilter(
                        pattern=lsp.FileOperationPattern(glob="**/*.py")
                    )
                ]
            ),
            lsp.ClientCapabilities(
                workspace=lsp.WorkspaceClientCapabilities(
                    file_operations=lsp.FileOperationClientCapabilities(did_rename=True)
                )
            ),
            server_capabilities(
                workspace=lsp.WorkspaceOptions(
                    workspace_folders=lsp.WorkspaceFoldersServerCapabilities(
                        supported=True, change_notifications=True
                    ),
                    file_operations=lsp.FileOperationOptions(
                        did_rename=lsp.FileOperationRegistrationOptions(
                            filters=[
                                lsp.FileOperationFilter(
                                    pattern=lsp.FileOperationPattern(glob="**/*.py")
                                )
                            ]
                        )
                    ),
                )
            ),
        ),
        (
            lsp.WORKSPACE_SYMBOL,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                workspace_symbol_provider=lsp.WorkspaceSymbolOptions(
                    resolve_provider=False,
                ),
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_DIAGNOSTIC,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                diagnostic_provider=lsp.DiagnosticOptions(
                    inter_file_dependencies=False,
                    workspace_diagnostics=False,
                ),
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_DIAGNOSTIC,
            lsp.DiagnosticOptions(
                workspace_diagnostics=True,
                inter_file_dependencies=True,
            ),
            lsp.ClientCapabilities(),
            server_capabilities(
                diagnostic_provider=lsp.DiagnosticOptions(
                    inter_file_dependencies=True,
                    workspace_diagnostics=False,
                ),
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_ON_TYPE_FORMATTING,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                document_on_type_formatting_provider=None,
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_ON_TYPE_FORMATTING,
            lsp.DocumentOnTypeFormattingOptions(first_trigger_character=":"),
            lsp.ClientCapabilities(),
            server_capabilities(
                document_on_type_formatting_provider=lsp.DocumentOnTypeFormattingOptions(
                    first_trigger_character=":",
                ),
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_INLINE_COMPLETION,
            None,
            lsp.ClientCapabilities(),
            server_capabilities(
                inline_completion_provider=None,
            ),
        ),
        (
            lsp.TEXT_DOCUMENT_INLINE_COMPLETION,
            lsp.InlineCompletionOptions(),
            lsp.ClientCapabilities(),
            server_capabilities(
                inline_completion_provider=lsp.InlineCompletionOptions(),
            ),
        ),
    ],
)
def test_register_feature(
    feature_manager: FeatureManager,
    method: str,
    options: Any,
    capabilities: lsp.ClientCapabilities,
    expected: lsp.ServerCapabilities,
):
    """Ensure that we can register features while specifying their associated
    options and that `pygls` is able to correctly build the corresponding server
    capabilities.

    Parameters
    ----------
    feature_manager
       The feature manager to use

    method
       The method to register the feature handler for.

    options
       The method options to use

    capabilities
       The client capabilities to use when building the server's capabilities.

    expected
       The expected server capabilties we are expecting to see.
    """

    @feature_manager.feature(method, options)
    def _():
        pass

    actual = ServerCapabilitiesBuilder(
        capabilities,
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
        ServerCapabilitiesBuilder.choose_position_encoding(capabilities),
    ).build()

    assert expected == actual


def test_register_prepare_rename_no_client_support(feature_manager: FeatureManager):
    @feature_manager.feature(lsp.TEXT_DOCUMENT_RENAME)
    def _():
        pass

    @feature_manager.feature(lsp.TEXT_DOCUMENT_PREPARE_RENAME)
    def _():
        pass

    expected = server_capabilities(rename_provider=True)

    actual = ServerCapabilitiesBuilder(
        lsp.ClientCapabilities(),
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
    ).build()

    assert expected == actual


def test_register_prepare_rename_with_client_support(feature_manager: FeatureManager):
    @feature_manager.feature(lsp.TEXT_DOCUMENT_RENAME)
    def _():
        pass

    @feature_manager.feature(lsp.TEXT_DOCUMENT_PREPARE_RENAME)
    def _():
        pass

    expected = server_capabilities(
        rename_provider=lsp.RenameOptions(prepare_provider=True)
    )

    actual = ServerCapabilitiesBuilder(
        lsp.ClientCapabilities(
            text_document=lsp.TextDocumentClientCapabilities(
                rename=lsp.RenameClientCapabilities(prepare_support=True)
            )
        ),
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
    ).build()

    assert expected == actual


def test_register_inlay_hint_resolve(feature_manager: FeatureManager):
    @feature_manager.feature(lsp.TEXT_DOCUMENT_INLAY_HINT)
    def _():
        pass

    @feature_manager.feature(lsp.INLAY_HINT_RESOLVE)
    def _():
        pass

    expected = server_capabilities(
        inlay_hint_provider=lsp.InlayHintOptions(resolve_provider=True),
    )

    actual = ServerCapabilitiesBuilder(
        lsp.ClientCapabilities(),
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
    ).build()

    assert expected == actual


def test_register_workspace_symbol_resolve(feature_manager: FeatureManager):
    @feature_manager.feature(lsp.WORKSPACE_SYMBOL)
    def _():
        pass

    @feature_manager.feature(lsp.WORKSPACE_SYMBOL_RESOLVE)
    def _():
        pass

    expected = server_capabilities(
        workspace_symbol_provider=lsp.WorkspaceSymbolOptions(resolve_provider=True),
    )

    actual = ServerCapabilitiesBuilder(
        lsp.ClientCapabilities(),
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
    ).build()

    assert expected == actual


def test_register_workspace_diagnostics(feature_manager: FeatureManager):
    @feature_manager.feature(
        lsp.TEXT_DOCUMENT_DIAGNOSTIC,
        lsp.DiagnosticOptions(
            identifier="example",
            inter_file_dependencies=False,
            workspace_diagnostics=False,
        ),
    )
    def _():
        pass

    @feature_manager.feature(lsp.WORKSPACE_DIAGNOSTIC)
    def _():
        pass

    expected = server_capabilities(
        diagnostic_provider=lsp.DiagnosticOptions(
            identifier="example",
            inter_file_dependencies=False,
            workspace_diagnostics=True,
        ),
    )

    actual = ServerCapabilitiesBuilder(
        lsp.ClientCapabilities(),
        feature_manager.features.keys(),
        feature_manager.feature_options,
        [],
        None,
        None,
    ).build()

    assert expected == actual
