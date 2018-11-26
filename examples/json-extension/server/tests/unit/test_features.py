import json

import pytest
from mock import Mock
from pygls.types import (DidCloseTextDocumentParams, DidOpenTextDocumentParams,
                         TextDocumentIdentifier, TextDocumentItem)
from pygls.workspace import Document, Workspace

from ...server import completions, did_close, did_open


class FakeServer():
    """We don't need real server to unit test features."""

    def __init__(self):
        self.workspace = Workspace('', None)


fake_document_uri = 'file://fake_doc.txt'
fake_document = Document(fake_document_uri, '')


server = FakeServer()
server.workspace.get_document = Mock(return_value=fake_document)

server.workspace.publish_diagnostics = Mock()
server.workspace.show_message = Mock()
server.workspace.show_message_log = Mock()


def _reset_mocks():
    server.workspace.publish_diagnostics.reset_mock()
    server.workspace.show_message.reset_mock()
    server.workspace.show_message_log.reset_mock()


def test_completions():
    completion_list = completions()
    labels = [i.label for i in completion_list.items]

    assert '"' in labels
    assert '[' in labels
    assert ']' in labels
    assert '{' in labels
    assert '}' in labels


def test_did_close():
    _reset_mocks()

    params = DidCloseTextDocumentParams(
        TextDocumentIdentifier(fake_document_uri))

    did_close(server, params)

    # Check if show message is called
    server.workspace.show_message.assert_called_once()


@pytest.mark.asyncio
async def test_did_open():
    _reset_mocks()

    # Document content
    doc_content = ''
    expected_msg = None

    # Get expected error message
    try:
        json.loads(doc_content)
    except json.JSONDecodeError as err:
        expected_msg = err.msg

    params = DidOpenTextDocumentParams(
        TextDocumentItem(fake_document_uri, '', 1, doc_content))

    await did_open(server, params)

    # Check publish diagnostics is called
    server.workspace.publish_diagnostics.assert_called_once()

    # Check publish diagnostics args message
    args = server.workspace.publish_diagnostics.call_args
    assert args[0][1][0].message is expected_msg

    # Check other methods are called
    server.workspace.show_message.assert_called_once()
    server.workspace.show_message_log.assert_called_once()
