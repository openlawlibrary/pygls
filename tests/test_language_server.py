# Copyright 2017 Palantir Technologies, Inc.
import os
from threading import Thread
import pytest
from pygls.ls import LanguageServer
from pygls.jsonrpc.exceptions import JsonRpcMethodNotFound
from pygls import lsp
from tests.ls_setup import setup_ls_features

CALL_TIMEOUT = 2


@pytest.fixture
def client_server():
    """ A fixture to setup a client/server """

    # Client to Server pipe
    csr, csw = os.pipe()
    # Server to client pipe
    scr, scw = os.pipe()

    # Setup server
    server = LanguageServer()
    setup_ls_features(server)

    server_thread = Thread(target=server.start_io, args=(
        os.fdopen(csr, 'rb'), os.fdopen(scw, 'wb')
    ))

    server_thread.daemon = True
    server_thread.start()

    # Setup client
    client = LanguageServer()

    client_thread = Thread(target=client.start_io, args=(
        os.fdopen(scr, 'rb'), os.fdopen(csw, 'wb')))

    client_thread.daemon = True
    client_thread.start()

    yield client, server

    shutdown_response = client._endpoint.request(
        'shutdown').result(timeout=CALL_TIMEOUT)
    assert shutdown_response is None
    client._endpoint.notify('exit')


def test_initialize(client_server):
    client, server = client_server
    response = client._endpoint.request('initialize', {
        'processId': 1234,
        'rootPath': os.path.dirname(__file__),
        'initializationOptions': {}
    }).result(timeout=CALL_TIMEOUT)
    assert 'capabilities' in response


def test_missing_message(client_server):
    client, server = client_server
    with pytest.raises(JsonRpcMethodNotFound):
        client._endpoint.request(
            'unknown_method').result(timeout=CALL_TIMEOUT)


def test_server_capabilities(client_server):
    client, server = client_server
    response = client._endpoint.request('initialize', {
        'processId': 1234,
        'rootPath': os.path.dirname(__file__),
        'initializationOptions': {}
    }).result(timeout=CALL_TIMEOUT)

    sc = response.get('capabilities', {})
