import asyncio
import json
import time
import uuid
from json import JSONDecodeError

from pygls.features import (
    COMPLETION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    ConfigurationItem,
    ConfigurationParams,
    Diagnostic,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    MessageType,
    Position,
    Range,
    Registration,
    RegistrationParams,
    Unregistration,
    UnregistrationParams,
)

__version__ = "1.0.0"

COUNT_DOWN_START_IN_SECONDS = 10
COUNT_DOWN_SLEEP_IN_SECONDS = 1


class JsonLanguageServer(LanguageServer):
    CMD_COUNT_DOWN_BLOCKING = "countDownBlocking"
    CMD_COUNT_DOWN_NON_BLOCKING = "countDownNonBlocking"
    CMD_REGISTER_COMPLETIONS = "registerCompletions"
    CMD_SHOW_CONFIGURATION_ASYNC = "showConfigurationAsync"
    CMD_SHOW_CONFIGURATION_CALLBACK = "showConfigurationCallback"
    CMD_SHOW_CONFIGURATION_THREAD = "showConfigurationThread"
    CMD_UNREGISTER_COMPLETIONS = "unregisterCompletions"

    CONFIGURATION_SECTION = "jsonServer"

    def __init__(self):
        super().__init__()


json_server = JsonLanguageServer()


def _validate(ls, params):
    ls.show_message_log("Validating json...")

    text_doc = ls.workspace.get_document(params.textDocument.uri)

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

        d = Diagnostic(
            Range(Position(line - 1, col - 1), Position(line - 1, col)),
            msg,
            source=type(json_server).__name__,
        )

        diagnostics.append(d)

    return diagnostics


@json_server.feature(COMPLETION, trigger_characters=[","])
def completions(params: CompletionParams = None):
    """Returns completion items."""
    return CompletionList(
        False,
        [
            CompletionItem('"'),
            CompletionItem("["),
            CompletionItem("]"),
            CompletionItem("{"),
            CompletionItem("}"),
        ],
    )


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    """Starts counting down and showing message synchronously.
    It will `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message("Counting down... {}".format(COUNT_DOWN_START_IN_SECONDS - i))
        time.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message("Counting down... {}".format(COUNT_DOWN_START_IN_SECONDS - i))
        await asyncio.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@json_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@json_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: JsonLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message("Text Document Did Close")


@json_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message("Text Document Did Open")
    _validate(ls, params)


@json_server.command(JsonLanguageServer.CMD_REGISTER_COMPLETIONS)
async def register_completions(ls: JsonLanguageServer, *args):
    """Register completions method on the client."""
    params = RegistrationParams(
        [Registration(str(uuid.uuid4()), COMPLETION, {"triggerCharacters": "[':']"})]
    )
    response = await ls.register_capability_async(params)
    if response is None:
        ls.show_message("Successfully registered completions method")
    else:
        ls.show_message(
            "Error happened during completions registration.", MessageType.Error
        )


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
async def show_configuration_async(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using coroutines."""
    try:
        config = await ls.get_configuration_async(
            ConfigurationParams(
                [ConfigurationItem("", JsonLanguageServer.CONFIGURATION_SECTION)]
            )
        )

        example_config = config[0].exampleConfiguration

        ls.show_message(
            "jsonServer.exampleConfiguration value: {}".format(example_config)
        )

    except Exception as e:
        ls.show_message_log("Error ocurred: {}".format(e))


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
def show_configuration_callback(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using callback."""

    def _config_callback(config):
        try:
            example_config = config[0].exampleConfiguration

            ls.show_message(
                "jsonServer.exampleConfiguration value: {}".format(example_config)
            )

        except Exception as e:
            ls.show_message_log("Error ocurred: {}".format(e))

    ls.get_configuration(
        ConfigurationParams(
            [ConfigurationItem("", JsonLanguageServer.CONFIGURATION_SECTION)]
        ),
        _config_callback,
    )


@json_server.thread()
@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
def show_configuration_thread(ls: JsonLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using thread pool."""
    try:
        config = ls.get_configuration(
            ConfigurationParams(
                [ConfigurationItem("", JsonLanguageServer.CONFIGURATION_SECTION)]
            )
        ).result(2)

        example_config = config[0].exampleConfiguration

        ls.show_message(
            "jsonServer.exampleConfiguration value: {}".format(example_config)
        )

    except Exception as e:
        ls.show_message_log("Error ocurred: {}".format(e))


@json_server.command(JsonLanguageServer.CMD_UNREGISTER_COMPLETIONS)
async def unregister_completions(ls: JsonLanguageServer, *args):
    """Unregister completions method on the client."""
    params = UnregistrationParams([Unregistration(str(uuid.uuid4()), COMPLETION)])
    response = await ls.unregister_capability_async(params)
    if response is None:
        ls.show_message("Successfully unregistered completions method")
    else:
        ls.show_message(
            "Error happened during completions unregistration.", MessageType.Error
        )


def run(host: str, port: int, tcp: bool, version: bool):
    """Run the Language Server."""
    if version:
        print(__version__)
        return

    print("Starting Language Server ...")

    if tcp:
        print(f"host: {host}, port: {port}")
        json_server.start_tcp(host, port)
    else:
        print("no tcp, starting on stdio")
        json_server.start_io()

    print("Exiting Language Server!")


def cli():
    import argparse

    ap = argparse.ArgumentParser(
        prog="JSON Language Server",
        description=("JSON Language Server implementing the Language Server Protocol."),
    )
    ap.add_argument(
        "-v", "--version", action="store_true", help="Print version and exit."
    )
    ap.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of stdio"
    )
    ap.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    ap.add_argument("--port", type=int, default=2087, help="Bind to this port")

    ns = ap.parse_args()
    run(**vars(ns))


if __name__ == "__main__":
    cli()
