import json

import pytest
from lsprotocol import types

from pygls.lsp.protocol import LanguageServerProtocol
from pygls.lsp.protocol import default_converter


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (
            types.TEXT_DOCUMENT_COMPLETION,
            types.CompletionParams(
                text_document=types.TextDocumentIdentifier(uri="file:///file.txt"),
                position=types.Position(line=1, character=0),
            ),
            {
                "jsonrpc": "2.0",
                "id": "1",
                "method": types.TEXT_DOCUMENT_COMPLETION,
                "params": {
                    "textDocument": {"uri": "file:///file.txt"},
                    "position": {"line": 1, "character": 0},
                },
            },
        ),
    ],
)
def test_encode_request(method, params, expected):
    """Ensure that we can encode request messages."""

    protocol = LanguageServerProtocol(default_converter)
    data = protocol.encode_request(method, params, msg_id="1", include_headers=False)
    actual = json.loads(data.decode("utf8"))

    assert actual == expected


@pytest.mark.parametrize(
    "msg_type, result, expected",
    [
        (types.ShutdownResponse, None, {"jsonrpc": "2.0", "id": "1", "result": None}),
        (
            types.TextDocumentCompletionResponse,
            [
                types.CompletionItem(label="example-one"),
                types.CompletionItem(
                    label="example-two",
                    kind=types.CompletionItemKind.Class,
                    preselect=False,
                    deprecated=True,
                ),
            ],
            {
                "jsonrpc": "2.0",
                "id": "1",
                "result": [
                    {"label": "example-one"},
                    {
                        "label": "example-two",
                        "kind": 7,  # CompletionItemKind.Class
                        "preselect": False,
                        "deprecated": True,
                    },
                ],
            },
        ),
    ],
)
def test_encode_response(msg_type, result, expected):
    """Ensure that we can serialize response messages"""

    protocol = LanguageServerProtocol(default_converter)
    protocol._result_types["1"] = msg_type

    data = protocol.encode_result("1", result=result, include_headers=False)
    actual = json.loads(data.decode("utf8"))

    assert actual == expected


@pytest.mark.parametrize(
    "method, params, expected",
    [
        (
            types.PROGRESS,
            types.ProgressParams(
                token="id1",
                value=types.WorkDoneProgressBegin(
                    title="Begin progress",
                    percentage=0,
                ),
            ),
            {
                "jsonrpc": "2.0",
                "method": "$/progress",
                "params": {
                    "token": "id1",
                    "value": {
                        "kind": "begin",
                        "percentage": 0,
                        "title": "Begin progress",
                    },
                },
            },
        ),
    ],
)
def test_encode_notification(method, params, expected):
    """Ensure that we can encode notification messages"""

    protocol = LanguageServerProtocol(default_converter)
    data = protocol.encode_notification(method, params=params, include_headers=False)
    actual = json.loads(data.decode("utf8"))

    assert actual == expected
