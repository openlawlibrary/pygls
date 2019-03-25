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
from pygls.protocol import to_lsp_name, deserialize_message
from pygls.types import InitializeResult

class dictToObj:
    def __init__(self, entries):
        self.__dict__.update(**entries)


def test_to_lsp_name():
    f_name = 'text_document__did_open'
    name = 'textDocument/didOpen'

    assert to_lsp_name(f_name) == name


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


def test_deserialize_message_with_reserved_words_should_pass_without_errors(client_server):
    params_with_reserved_word = '''
    {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {
            "__dummy__": true
        }
    }
    '''
    obj = json.loads(params_with_reserved_word,
                     object_hook=deserialize_message)
    assert isinstance(obj, object)
    assert "_0" in dir(obj.params)
