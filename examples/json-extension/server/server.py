##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import asyncio
import json
import time
from json import JSONDecodeError

from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN)
from pygls.server import LanguageServer
from pygls.types import (CompletionItem, CompletionList, CompletionParams,
                         ConfigurationItem, ConfigurationParams, Diagnostic,
                         DidChangeTextDocumentParams,
                         DidCloseTextDocumentParams, DidOpenTextDocumentParams,
                         Position, Range)


class JsonLanguageServer(LanguageServer):
    CMD_COUNT_DOWN_BLOCKING = 'countDownBlocking'
    CMD_COUNT_DOWN_NON_BLOCKING = 'countDownNonBlocking'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_SHOW_CONFIGURATION_CALLBACK = 'showConfigurationCallback'
    CMD_SHOW_CONFIGURATION_THREAD = 'showConfigurationThread'

    CONFIGURATION_SECTION = 'jsonServer'

    def __init__(self):
        super().__init__()


json_server = JsonLanguageServer()


def _validate(ls, params):
    ls.show_message_log('Validating json...')

    text_doc = ls.workspace.get_document(params.textDocument.uri)

    diagnostics = _validate_json(text_doc)

    ls.publish_diagnostics(text_doc.uri, diagnostics)


def _validate_json(doc):
    """Validates json file."""
    diagnostics = []

    try:
        json.loads(doc.source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = Diagnostic(
            Range(
                Position(line-1, col-1),
                Position(line-1, col)
            ),
            msg,
            source=type(json_server).__name__
        )

        diagnostics.append(d)

    return diagnostics


@json_server.feature(COMPLETION, trigger_characters=[','])
def completions(params: CompletionParams = None):
    """Returns completion items."""
    return CompletionList(False, [
        CompletionItem('"'),
        CompletionItem('['),
        CompletionItem(']'),
        CompletionItem('{'),
        CompletionItem('}')
    ])


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    """Starts counting down and showing message synchronously.
    It will `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(10):
        ls.show_message('Counting down... {}'.format(10 - i))
        time.sleep(1)


@json_server.command(JsonLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(10):
        ls.show_message('Counting down... {}'.format(10 - i))
        await asyncio.sleep(1)


@json_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@json_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: JsonLanguageServer, params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message('Text Document Did Close')


@json_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Text Document Did Open')
    _validate(ls, params)


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
async def show_python_path_async(ls: JsonLanguageServer, *args):
    """Gets python path from configuration and displays it."""
    try:
        config = await ls.get_configuration_async(ConfigurationParams([
            ConfigurationItem('', 'jsonServer')
        ]))

        example_config = config[0].exampleConfiguration

        ls.show_message(
            'jsonServer.exampleConfiguration value: {}'.format(example_config)
        )

    except Exception as e:
        ls.show_message_log('Error ocurred: {}'.format(e))


@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
def show_python_path_callback(ls: JsonLanguageServer, *args):
    """Gets python path from configuration and displays it."""
    def _config_callback(config):
        try:
            example_config = config[0].exampleConfiguration

            ls.show_message(
                'jsonServer.exampleConfiguration value: {}'
                .format(example_config)
            )

        except Exception as e:
            ls.show_message_log('Error ocurred: {}'.format(e))

    ls.get_configuration(ConfigurationParams([
        ConfigurationItem('', 'jsonServer')
    ]), _config_callback)


@json_server.thread()
@json_server.command(JsonLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
def show_python_path_thread(ls: JsonLanguageServer, *args):
    """Gets python path from configuration and displays it."""
    try:
        config = ls.get_configuration(ConfigurationParams([
            ConfigurationItem('', 'jsonServer')
        ])).result(2)

        example_config = config[0].exampleConfiguration

        ls.show_message(
            'jsonServer.exampleConfiguration value: {}'.format(example_config)
        )

    except Exception as e:
        ls.show_message_log('Error ocurred: {}'.format(e))
