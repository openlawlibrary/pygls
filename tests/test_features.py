'''
This module tests if registered features are called
'''

from pygls import lsp
from tests.test_language_server import client_server

CALL_TIMEOUT = 2


def test_completions(client_server):
    client, server = client_server

    kwargs = {
        'textDocument': 'test',
        'position': 'test'
    }

    response = client._endpoint.request(
        lsp.COMPLETION, kwargs).result(timeout=CALL_TIMEOUT)

    assert response == kwargs


def test_completion_item_resolve(client_server):
    client, server = client_server

    kwargs = {
        'completionItem': {
            'label': 'test'
        }
    }

    response = client._endpoint.request(
        lsp.COMPLETION_ITEM_RESOLVE, kwargs).result(timeout=CALL_TIMEOUT)

    assert response == kwargs


def test_hover(client_server):
    client, server = client_server

    kwargs = {
        'textDocument': 'test',
        'position': 'test'
    }

    response = client._endpoint.request(
        lsp.HOVER, kwargs).result(timeout=CALL_TIMEOUT)

    assert response == kwargs
