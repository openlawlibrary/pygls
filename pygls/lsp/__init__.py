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
from typing import Any, Union

import attrs
from lsprotocol.types import METHOD_TO_TYPES
from typeguard import check_type

from pygls.exceptions import MethodTypeNotRegisteredError

@attrs.define
class JsonRPCNotification:
    """A class that represents json rpc notification message."""

    jsonrpc: str
    method: str
    params: Any

@attrs.define
class JsonRPCRequestMessage:
    """A class that represents json rpc request message."""

    jsonrpc: str
    id: Union[int, str]
    method: str
    params: Any


@attrs.define
class JsonRPCResponseMessage:
    """A class that represents json rpc response message."""

    jsonrpc: str
    id: Union[int, str]
    result: Union[Any, None] = attrs.field(default=None)


def get_method_registration_options_type(method_name, lsp_methods_map=METHOD_TO_TYPES):
    try:
        return lsp_methods_map[method_name][3]
    except KeyError:
        raise MethodTypeNotRegisteredError(method_name)


def get_method_params_type(method_name, lsp_methods_map=METHOD_TO_TYPES):
    try:
        return lsp_methods_map[method_name][2]
    except KeyError:
        raise MethodTypeNotRegisteredError(method_name)


def get_method_return_type(method_name, lsp_methods_map=METHOD_TO_TYPES):
    try:
        return lsp_methods_map[method_name][1]
    except KeyError:
        raise MethodTypeNotRegisteredError(method_name)


def is_instance(o, t):
    try:
        check_type('', o, t)
        return True
    except TypeError:
        return False
