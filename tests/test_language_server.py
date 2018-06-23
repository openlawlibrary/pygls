# Copyright 2017 Palantir Technologies, Inc.
import os
from threading import Thread
import pytest
from pygls.ls import LanguageServer
from pygls.jsonrpc.exceptions import JsonRpcMethodNotFound
from pygls import lsp

from tests.ls_setup import setup_ls_features
from tests import DUMMY_FEATURE, TRIGGER_CHARS, COMMANDS

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

    assert sc.get('hoverProvider') is True
    assert sc.get('completionProvider').get('resolveProvider') is True
    assert sc.get('completionProvider').get(
        'triggerCharacters') == TRIGGER_CHARS
    assert sc.get('signatureHelpProvider').get(
        'triggerCharacters') == TRIGGER_CHARS
    assert sc.get('definitionProvider') is True
    # assert sc.get('typeDefinitionProvider') is True
    # assert sc.get('implementationProvider') is True
    assert sc.get('referencesProvider') is True
    assert sc.get('documentHighlightProvider') is True
    assert sc.get('documentSymbolProvider') is True
    assert sc.get('workspaceSymbolProvider') is True
    assert sc.get('codeActionProvider') is True
    assert sc.get('codeLensProvider').get('resolveProvider') is True
    assert sc.get('documentFormattingProvider') is True
    assert sc.get('documentRangeFormattingProvider') is True
    # assert sc.get('documentOnTypeFormattingProvider') is True
    assert sc.get('renameProvider') is True
    assert sc.get('documentLinkProvider').get('resolveProvider') is True
    # assert sc.get('colorProvider') is True
    assert sc.get('executeCommandProvider').get('commands') == COMMANDS
    assert sc.get('workspace').get('workspaceFolders').get('supported') is True
    assert sc.get('workspace').get('workspaceFolders').get(
        'changeNotifications') is True


def test_feature_is_called(client_server):
    client, server = client_server

    is_called = client._endpoint.request(
        lsp.COMPLETION).result(timeout=CALL_TIMEOUT)

    assert is_called


def test_feature_params(client_server):
    client, server = client_server

    # Add dummy feature just to test this case
    @server.feature(DUMMY_FEATURE)
    def dummy_feature(param1=None, param2=None, **_kwargs):
        return {
            'param1': param1,
            'param2': param2
        }

    kwargs = {
        'param1': 'test',
        'param2': True
    }

    response = client._endpoint.request(
        DUMMY_FEATURE, kwargs).result(timeout=CALL_TIMEOUT)

    assert response == kwargs


def test_ls_instance_is_passed_to_user_defined_features(client_server):
    client, server = client_server

    # Add dummy feature just to test this case
    @server.feature(DUMMY_FEATURE)
    def dummy_feature(ls, param1=None, param2=None, **_kwargs):
        return id(ls)

    response = client._endpoint.request(
        DUMMY_FEATURE).result(timeout=CALL_TIMEOUT)

    assert response == id(server)


def test_users_feature_called_after_same_default_feature(client_server):
    client, server = client_server

    is_called = [False]

    @server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
    def tx_doc_did_open(ls, textDocument=None, **_kwargs):
        '''
            Since this is notification, there is no response
        '''
        is_called[0] = True

    # Initialize server's workspace
    response = client._endpoint.request('initialize', {
        'processId': 1234,
        'rootPath': os.path.dirname(__file__),
        'initializationOptions': {}
    }).result(timeout=CALL_TIMEOUT)

    kwargs = {
        'textDocument': {
            'uri': 'C:\\test',
            'text': 'test'
        }
    }
    client._endpoint.request(
        lsp.TEXT_DOCUMENT_DID_OPEN, kwargs).result(timeout=CALL_TIMEOUT)

    assert is_called[0] is True


def test_registered_commands(client_server):
    client, server = client_server

    assert list(server.commands.keys()) == COMMANDS

    add_cmd = COMMANDS[0]

    kwargs = {
        'command': add_cmd,
        'arguments': [1, 2]
    }

    response = client._endpoint.request(
        lsp.WORKSPACE_EXECUTE_COMMAND, kwargs).result(timeout=CALL_TIMEOUT)

    assert response == 3
