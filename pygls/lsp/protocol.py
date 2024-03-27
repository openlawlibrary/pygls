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
from typing import Optional
from typing import Type

import cattrs
from lsprotocol import converters
from lsprotocol import types

from pygls.protocol import json_rpc

MsgId = json_rpc.MsgId


def default_converter() -> cattrs.Converter:
    """Default converter factory for LSP types."""
    converter = converters.get_converter()
    return converter


class LanguageServerProtocol(json_rpc.JsonRPCProtocol):
    """LSP Protocol."""

    def __init__(
        self,
        *args,
        converter_factory: json_rpc.ConverterFactory = default_converter,
        **kwargs,
    ):
        super().__init__(converter_factory=converter_factory, **kwargs)

    def get_notification_type(
        self, method: str
    ) -> Optional[Type[json_rpc.JsonRPCNotification]]:
        """Return the type definition of the notification associated with the given
        method."""
        return types.METHOD_TO_TYPES.get(method, (None,))[0]

    def get_request_type(
        self, method: str
    ) -> Optional[Type[json_rpc.JsonRPCRequestMessage]]:
        """Return the type definition of the result associated with the given method."""
        return types.METHOD_TO_TYPES.get(method, (None,))[0]

    def get_result_type(
        self, method: str
    ) -> Optional[Type[json_rpc.JsonRPCResultMessage]]:
        """Return the type definition of the result associated with the given method."""
        return types.METHOD_TO_TYPES.get(method, (None, None))[1]
