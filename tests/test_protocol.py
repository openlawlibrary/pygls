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
import json

import pytest
from pygls.protocol import (JsonRPCNotification, JsonRPCRequestMessage,
                            JsonRPCResponseMessage, deserialize_message,
                            to_lsp_name)
from pygls.types import InitializeResult


class dictToObj:
    def __init__(self, entries):
        self.__dict__.update(**entries)


def test_deserialize_message_with_reserved_words_should_pass_without_errors(client_server):
    params = '''
    {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {
            "__dummy__": true
        }
    }
    '''
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCNotification)
    assert result.params._0 is True


def test_deserialize_message_should_return_notification_message():
    params = '''
    {
        "jsonrpc": "2.0",
        "method": "test",
        "params": "1"
    }
    '''
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCNotification)
    assert result.jsonrpc == "2.0"
    assert result.method == "test"
    assert result.params == "1"


def test_deserialize_message_without_jsonrpc_field__should_return_object():
    params = '''
    {
        "random": "data",
        "def": "def"
    }
    '''
    result = json.loads(params, object_hook=deserialize_message)

    assert type(result).__name__ == 'Object'
    assert result.random == "data"

    # namedtuple does not guarantee field order
    try:
        assert result._0 == "def"
    except AttributeError:
        assert result._1 == "def"


def test_deserialize_message_should_return_response_message():
    params = '''
    {
        "jsonrpc": "2.0",
        "id": "id",
        "result": "1"
    }
    '''
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCResponseMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.result == "1"
    assert result.error is None


def test_deserialize_message_should_return_request_message():
    params = '''
    {
        "jsonrpc": "2.0",
        "id": "id",
        "method": "test",
        "params": "1"
    }
    '''
    result = json.loads(params, object_hook=deserialize_message)

    assert isinstance(result, JsonRPCRequestMessage)
    assert result.jsonrpc == "2.0"
    assert result.id == "id"
    assert result.method == "test"
    assert result.params == "1"


def test_initialize_without_capabilities_should_raise_error(client_server):
    _, server = client_server
    params = dictToObj({
        "processId": 1234,
        "rootUri": None
    })
    with pytest.raises(Exception):
        server.lsp.bf_initialize(params)


def test_initialize_without_process_id_should_raise_error(client_server):
    _, server = client_server
    params = dictToObj({
        "capabilities": {},
        "rootUri": None
    })
    with pytest.raises(Exception):
        server.lsp.bf_initialize(params)


def test_initialize_without_root_uri_should_raise_error(client_server):
    _, server = client_server
    params = dictToObj({
        "capabilities": {},
        "processId": 1234,
    })
    with pytest.raises(Exception):
        server.lsp.bf_initialize(params)


def test_initialize_should_return_server_capabilities(client_server):
    _, server = client_server
    params = dictToObj({
        "capabilities": {},
        "processId": 1234,
        "rootUri": None
    })

    server_capabilities = server.lsp.bf_initialize(params)

    assert isinstance(server_capabilities, InitializeResult)


def test_response_object_fields():
    # Result field set
    response = JsonRPCResponseMessage(0, '2.0', 'result', None).without_none_fields()

    assert hasattr(response, 'id')
    assert hasattr(response, 'jsonrpc')
    assert hasattr(response, 'result')
    assert not hasattr(response, 'error')

    # Error field set
    response = JsonRPCResponseMessage(0, '2.0', None, 'error').without_none_fields()

    assert hasattr(response, 'id')
    assert hasattr(response, 'jsonrpc')
    assert hasattr(response, 'error')
    assert not hasattr(response, 'result')


def test_to_lsp_name():
    f_name = 'text_document__did_open'
    name = 'textDocument/didOpen'

    assert to_lsp_name(f_name) == name
