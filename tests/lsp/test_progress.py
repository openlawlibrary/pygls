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

from typing import List, Optional

import time
from pygls.lsp.methods import CODE_LENS, PROGRESS_NOTIFICATION
from pygls.lsp.types import (
    CodeLens,
    CodeLensParams,
    CodeLensOptions,
    TextDocumentIdentifier,
    WorkDoneProgressBegin,
    WorkDoneProgressEnd,
    WorkDoneProgressReport,
)
from pygls.lsp.types.basic_structures import ProgressParams
from ..conftest import ClientServer


PROGRESS_TOKEN = "token"


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()
        self.client.notifications: List[ProgressParams] = []

        @self.server.feature(
            CODE_LENS,
            CodeLensOptions(resolve_provider=False,
                            work_done_progress=PROGRESS_TOKEN),
        )
        def f1(params: CodeLensParams) -> Optional[List[CodeLens]]:
            self.server.lsp.progress.begin(
                PROGRESS_TOKEN, WorkDoneProgressBegin(
                    title="starting", percentage=0)
            )
            self.server.lsp.progress.report(
                PROGRESS_TOKEN,
                WorkDoneProgressReport(message="doing", percentage=50),
            )
            self.server.lsp.progress.end(
                PROGRESS_TOKEN, WorkDoneProgressEnd(message="done")
            )
            return None

        @self.client.feature(PROGRESS_NOTIFICATION)
        def f2(params):
            self.client.notifications.append(params)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    provider = capabilities.code_lens_provider
    assert provider
    assert provider.work_done_progress == PROGRESS_TOKEN


@ConfiguredLS.decorate()
def test_progress_notifications(client_server):
    client, _ = client_server
    client.lsp.send_request(
        CODE_LENS,
        CodeLensParams(
            text_document=TextDocumentIdentifier(uri="file://return.none"),
            work_done_token=PROGRESS_TOKEN,
        ),
    ).result()

    time.sleep(0.1)

    assert len(client.notifications) == 3
    assert client.notifications[0].token == PROGRESS_TOKEN
    assert client.notifications[0].value == {
        "kind": "begin",
        "title": "starting",
        "percentage": 0,
    }
    assert client.notifications[1].value == {
        "kind": "report",
        "message": "doing",
        "percentage": 50,
    }
    assert client.notifications[2].value == {
        "kind": "end", "message": "done"}
