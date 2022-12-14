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

from typing import List

import time
from lsprotocol.types import (
    TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS,
    PublishDiagnosticsParams,
    Diagnostic,
    Range,
    Position,
)
from ..conftest import ClientServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()
        self.client.notifications: List[PublishDiagnosticsParams] = []

        @self.client.feature(TEXT_DOCUMENT_PUBLISH_DIAGNOSTICS)
        def f1(params: PublishDiagnosticsParams):
            self.client.notifications.append(params)


@ConfiguredLS.decorate()
def test_diagnostics_notifications(client_server):
    client, server = client_server
    diagnostic = Diagnostic(
        range=Range(
            start=Position(line=0, character=0),
            end=Position(line=1, character=1),
        ),
        message="test diagnostic",
    )
    server.lsp.publish_diagnostics(
        PublishDiagnosticsParams(uri="", diagnostics=[diagnostic], version=1),
    )
    server.lsp.publish_diagnostics(
        "",
        diagnostics=[diagnostic],
        version=1,
    )

    time.sleep(0.1)

    assert len(client.notifications) == 2
    expected = PublishDiagnosticsParams(
        uri="",
        diagnostics=[diagnostic],
        version=1,
    )
    assert client.notifications[0] == expected


@ConfiguredLS.decorate()
def test_diagnostics_notifications_deprecated(client_server):
    client, server = client_server
    diagnostic = Diagnostic(
        range=Range(
            start=Position(line=0, character=0),
            end=Position(line=1, character=1),
        ),
        message="test diagnostic",
    )
    server.publish_diagnostics(
        "",
        diagnostics=[diagnostic],
        version=1,
    )

    time.sleep(0.1)

    assert len(client.notifications) == 1
    expected = PublishDiagnosticsParams(
        uri="",
        diagnostics=[diagnostic],
        version=1,
    )
    assert client.notifications[0] == expected
