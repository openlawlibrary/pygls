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

from typing import Any, List, Union
import time

import pytest

from pygls.exceptions import JsonRpcInternalError, PyglsError, JsonRpcException
from lsprotocol.types import WINDOW_SHOW_MESSAGE, MessageType
from pygls.server import LanguageServer

from ..conftest import ClientServer

ERROR_TRIGGER = "test/triggerError"
ERROR_MESSAGE = "Testing errors"


class CustomLanguageServerSafe(LanguageServer):
    def report_server_error(
        self, error: Exception, source: Union[PyglsError, JsonRpcException]
    ):
        pass


class CustomLanguageServerPotentialRecursion(LanguageServer):
    def report_server_error(
        self, error: Exception, source: Union[PyglsError, JsonRpcException]
    ):
        raise Exception()


class CustomLanguageServerSendAll(LanguageServer):
    def report_server_error(
        self, error: Exception, source: Union[PyglsError, JsonRpcException]
    ):
        self.show_message(self.default_error_message, msg_type=MessageType.Error)


class ConfiguredLS(ClientServer):
    def __init__(self, LS=LanguageServer):
        super().__init__(LS)
        self.init()

    def init(self):
        self.client.messages: List[str] = []

        @self.server.feature(ERROR_TRIGGER)
        def f1(params: Any):
            raise Exception(ERROR_MESSAGE)

        @self.client.feature(WINDOW_SHOW_MESSAGE)
        def f2(params: Any):
            self.client.messages.append(params.message)


class CustomConfiguredLSSafe(ConfiguredLS):
    def __init__(self):
        super().__init__(CustomLanguageServerSafe)


class CustomConfiguredLSPotentialRecusrion(ConfiguredLS):
    def __init__(self):
        super().__init__(CustomLanguageServerPotentialRecursion)


class CustomConfiguredLSSendAll(ConfiguredLS):
    def __init__(self):
        super().__init__(CustomLanguageServerSendAll)


@ConfiguredLS.decorate()
def test_request_error_reporting_default(client_server):
    client, _ = client_server
    assert len(client.messages) == 0

    with pytest.raises(JsonRpcInternalError, match=ERROR_MESSAGE):
        client.lsp.send_request(ERROR_TRIGGER).result()

    time.sleep(0.1)
    assert len(client.messages) == 0


@CustomConfiguredLSSendAll.decorate()
def test_request_error_reporting_override(client_server):
    client, _ = client_server
    assert len(client.messages) == 0

    with pytest.raises(JsonRpcInternalError, match=ERROR_MESSAGE):
        client.lsp.send_request(ERROR_TRIGGER).result()

    time.sleep(0.1)
    assert len(client.messages) == 1


@ConfiguredLS.decorate()
def test_notification_error_reporting(client_server):
    client, _ = client_server
    client.lsp.notify(ERROR_TRIGGER)
    time.sleep(0.1)

    assert len(client.messages) == 1
    assert client.messages[0] == LanguageServer.default_error_message


@CustomConfiguredLSSafe.decorate()
def test_overriding_error_reporting(client_server):
    client, _ = client_server
    client.lsp.notify(ERROR_TRIGGER)
    time.sleep(0.1)

    assert len(client.messages) == 0


@CustomConfiguredLSPotentialRecusrion.decorate()
def test_overriding_error_reporting_with_potential_recursion(client_server):
    client, _ = client_server
    client.lsp.notify(ERROR_TRIGGER)
    time.sleep(0.1)

    assert len(client.messages) == 0
