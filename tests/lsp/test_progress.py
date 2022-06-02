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
import unittest
from typing import List, Optional

import time
from pygls.lsp.methods import (
    CODE_LENS,
    PROGRESS_NOTIFICATION

)
from pygls.lsp.types import (
    CodeLens,
    CodeLensParams,
    CodeLensOptions,
    TextDocumentIdentifier,
    WorkDoneProgressBegin,
    WorkDoneProgressEnd,
    WorkDoneProgressReport
)
from pygls.lsp.types.basic_structures import ProgressParams
from ..conftest import CALL_TIMEOUT, ClientServer


PROGRESS_TOKEN = 'token'


class TestCodeLens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_server = ClientServer()
        cls.client, cls.server = cls.client_server
        cls.notifications: List[ProgressParams] = []

        @cls.server.feature(
            CODE_LENS,
            CodeLensOptions(
                resolve_provider=False,
                work_done_progress=PROGRESS_TOKEN
            ),
        )
        def f1(params: CodeLensParams) -> Optional[List[CodeLens]]:
            cls.server.lsp.progress.begin(
                PROGRESS_TOKEN,
                WorkDoneProgressBegin(title='starting', percentage=0)
            )
            cls.server.lsp.progress.report(
                PROGRESS_TOKEN,
                WorkDoneProgressReport(message='doing', percentage=50),
            )
            cls.server.lsp.progress.end(
                PROGRESS_TOKEN,
                WorkDoneProgressEnd(message='done')
            )
            return None

        @cls.client.feature(
            PROGRESS_NOTIFICATION
        )
        def f2(params):
            cls.notifications.append(params)

        cls.client_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.client_server.stop()

    def test_capabilities(self):
        capabilities = self.server.server_capabilities

        assert capabilities.code_lens_provider
        assert capabilities.code_lens_provider.work_done_progress == PROGRESS_TOKEN

    def test_progress_notifications(self):
        self.client.lsp.send_request(
            CODE_LENS,
            CodeLensParams(
                text_document=TextDocumentIdentifier(uri='file://return.none'),
                work_done_token=PROGRESS_TOKEN
            ),
        ).result(timeout=CALL_TIMEOUT)

        time.sleep(0.1)

        assert len(self.notifications) == 3
        assert self.notifications[0].token == PROGRESS_TOKEN
        assert self.notifications[0].value == {
            'kind': 'begin', 'title': 'starting', 'percentage': 0
        }
        assert self.notifications[1].value == {
            'kind': 'report', 'message': 'doing', 'percentage': 50
        }
        assert self.notifications[2].value == {
            'kind': 'end', 'message': 'done'
        }


if __name__ == '__main__':
    unittest.main()
