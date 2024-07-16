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
"""In addition to implementing a variety of LSP methods, this larger example
demonstrates a number of pygls' capabilities including

- Defining custom commands
- Progress updates
- Fetching configuration values from the client
- Running methods in a thread
- Async methods
- Dynamic method (un)registration
- Starting a TCP/WebSocket server.

This is left over from a time where *pygls* tried to have a single example server to
demonstrate all of its features.
Eventually this example will be broken up in smaller, more focused examples and how to
guides.
"""
import argparse
import asyncio
import json
import time
import uuid
from json import JSONDecodeError
from typing import Optional

from lsprotocol import types as lsp

from pygls.server import LanguageServer

COUNT_DOWN_START_IN_SECONDS = 10
COUNT_DOWN_SLEEP_IN_SECONDS = 1


class JsonLanguageServer(LanguageServer):
    CMD_COUNT_DOWN_BLOCKING = "countDownBlocking"
    CMD_COUNT_DOWN_NON_BLOCKING = "countDownNonBlocking"
    CMD_PROGRESS = "progress"
    CMD_REGISTER_COMPLETIONS = "registerCompletions"
    CMD_SHOW_CONFIGURATION_ASYNC = "showConfigurationAsync"
    CMD_SHOW_CONFIGURATION_CALLBACK = "showConfigurationCallback"
    CMD_SHOW_CONFIGURATION_THREAD = "showConfigurationThread"
    CMD_UNREGISTER_COMPLETIONS = "unregisterCompletions"

    CONFIGURATION_SECTION = "pygls.jsonServer"

    def __init__(self, *args):
        super().__init__(*args)


json_server = JsonLanguageServer("pygls-json-example", "v0.1")


def _validate(ls, params):
    ls.show_message_log("Validating json...")

    text_doc = ls.workspace.get_document(params.text_document.uri)

    source = text_doc.source
    diagnostics = _validate_json(source) if source else []

    ls.publish_diagnostics(text_doc.uri, diagnostics)


def _validate_json(source):
    """Validates json file."""
    diagnostics = []

    try:
        json.loads(source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = lsp.Diagnostic(
            range=lsp.Range(
                start=lsp.Position(line=line - 1, character=col - 1),
                end=lsp.Position(line=line - 1, character=col),
            ),
            message=msg,
            source=type(json_server).__name__,
        )

        diagnostics.append(d)

    return diagnostics


@json_server.feature(
    lsp.TEXT_DOCUMENT_DIAGNOSTIC,
    lsp.DiagnosticOptions(
        identifier="jsonServer",
        inter_file_dependencies=True,
        workspace_diagnostics=True,
    ),
)
def text_document_diagnostic(
    params: lsp.DocumentDiagnosticParams,
) -> lsp.DocumentDiagnosticReport:
    """Returns diagnostic report."""
    document = json_server.workspace.get_document(params.text_document.uri)
    return lsp.RelatedFullDocumentDiagnosticReport(
        items=_validate_json(document.source),
        kind=lsp.DocumentDiagnosticReportKind.Full,
    )


@json_server.feature(lsp.WORKSPACE_DIAGNOSTIC)
def workspace_diagnostic(
    params: lsp.WorkspaceDiagnosticParams,
) -> lsp.WorkspaceDiagnosticReport:
    """Returns diagnostic report."""
    documents = json_server.workspace.text_documents.keys()

    if len(documents) == 0:
        items = []
    else:
        first = list(documents)[0]
        document = json_server.workspace.get_document(first)
        items = [
            lsp.WorkspaceFullDocumentDiagnosticReport(
                uri=document.uri,
                version=document.version,
                items=_validate_json(document.source),
                kind=lsp.DocumentDiagnosticReportKind.Full,
            )
        ]

    return lsp.WorkspaceDiagnosticReport(items=items)


@json_server.feature(
    lsp.TEXT_DOCUMENT_COMPLETION,
    lsp.CompletionOptions(trigger_characters=[","], all_commit_characters=[":"]),
)
def completions(params: Optional[lsp.CompletionParams] = None) -> lsp.CompletionList:
    """Returns completion items."""
    return lsp.CompletionList(
        is_incomplete=False,
        items=[
            lsp.CompletionItem(label='"'),
            lsp.CompletionItem(label="["),
            lsp.CompletionItem(label="]"),
            lsp.CompletionItem(label="{"),
            lsp.CompletionItem(label="}"),
        ],
    )


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    """Starts counting down and showing message synchronously.
    It will `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(f"Counting down... {COUNT_DOWN_START_IN_SECONDS - i}")
        time.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(f"Counting down... {COUNT_DOWN_START_IN_SECONDS - i}")
        await asyncio.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@json_server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: lsp.DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@json_server.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: JsonLanguageServer, params: lsp.DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message("Text Document Did Close")


@json_server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: lsp.DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message("Text Document Did Open")
    _validate(ls, params)


@json_server.feature(lsp.TEXT_DOCUMENT_INLINE_VALUE)
def inline_value(params: lsp.InlineValueParams):
    """Returns inline value."""
    return [lsp.InlineValueText(range=params.range, text="Inline value")]


@json_server.command(JsonLanguageServer.CMD_PROGRESS)
async def progress(ls: JsonLanguageServer, *args):
    """Create and start the progress on the client."""
    token = str(uuid.uuid4())
    # Create
    await ls.progress.create_async(token)
    # Begin
    ls.progress.begin(
        token,
        lsp.WorkDoneProgressBegin(title="Indexing", percentage=0, cancellable=True),
    )
    # Report
    for i in range(1, 10):
        # Check for cancellation from client
        if ls.progress.tokens[token].cancelled():
            # ... and stop the computation if client cancelled
            return
        ls.progress.report(
            token,
            lsp.WorkDoneProgressReport(message=f"{i * 10}%", percentage=i * 10),
        )
        await asyncio.sleep(2)
    # End
    ls.progress.end(token, lsp.WorkDoneProgressEnd(message="Finished"))


@json_server.command(JsonLanguageServer.CMD_REGISTER_COMPLETIONS)
async def register_completions(ls: JsonLanguageServer, *args):
    """Register completions method on the client."""
    params = lsp.RegistrationParams(
        registrations=[
            lsp.Registration(
                id=str(uuid.uuid4()),
                method=lsp.TEXT_DOCUMENT_COMPLETION,
                register_options={"triggerCharacters": "[':']"},
            )
        ]
    )
    response = await ls.register_capability_async(params)
    if response is None:
        ls.show_message("Successfully registered completions method")
    else:
        ls.show_message(
            "Error happened during completions registration.", lsp.MessageType.Error
        )


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
async def show_configuration_async(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using coroutines."""
    try:
        config = await ls.get_configuration_async(
            lsp.WorkspaceConfigurationParams(
                items=[
                    lsp.ConfigurationItem(
                        scope_uri="", section=JsonLanguageServer.CONFIGURATION_SECTION
                    )
                ]
            )
        )

        example_config = config[0].get("exampleConfiguration")

        ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

    except Exception as e:
        ls.show_message_log(f"Error ocurred: {e}")


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
def show_configuration_callback(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using callback."""

    def _config_callback(config):
        try:
            example_config = config[0].get("exampleConfiguration")

            ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

        except Exception as e:
            ls.show_message_log(f"Error ocurred: {e}")

    ls.get_configuration(
        lsp.WorkspaceConfigurationParams(
            items=[
                lsp.ConfigurationItem(
                    scope_uri="", section=JsonLanguageServer.CONFIGURATION_SECTION
                )
            ]
        ),
        _config_callback,
    )


@json_server.thread()
@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
def show_configuration_thread(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using thread pool."""
    try:
        config = ls.get_configuration(
            lsp.WorkspaceConfigurationParams(
                items=[
                    lsp.ConfigurationItem(
                        scope_uri="", section=JsonLanguageServer.CONFIGURATION_SECTION
                    )
                ]
            )
        ).result(2)

        example_config = config[0].get("exampleConfiguration")

        ls.show_message(f"jsonServer.exampleConfiguration value: {example_config}")

    except Exception as e:
        ls.show_message_log(f"Error ocurred: {e}")


@json_server.command(JsonLanguageServer.CMD_UNREGISTER_COMPLETIONS)
async def unregister_completions(ls: JsonLanguageServer, *args):
    """Unregister completions method on the client."""
    params = lsp.UnregistrationParams(
        unregisterations=[
            lsp.Unregistration(
                id=str(uuid.uuid4()), method=lsp.TEXT_DOCUMENT_COMPLETION
            )
        ]
    )
    response = await ls.unregister_capability_async(params)
    if response is None:
        ls.show_message("Successfully unregistered completions method")
    else:
        ls.show_message(
            "Error happened during completions unregistration.", lsp.MessageType.Error
        )


def add_arguments(parser):
    parser.description = "simple json server example"

    parser.add_argument("--tcp", action="store_true", help="Use TCP server")
    parser.add_argument("--ws", action="store_true", help="Use WebSocket server")
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", type=int, default=2087, help="Bind to this port")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.tcp:
        json_server.start_tcp(args.host, args.port)
    elif args.ws:
        json_server.start_ws(args.host, args.port)
    else:
        json_server.start_io()


if __name__ == "__main__":
    main()
