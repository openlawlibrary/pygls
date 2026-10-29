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

import asyncio
from typing import List, Optional
from unittest.mock import Mock

import pytest
from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_LENS,
    WINDOW_WORK_DONE_PROGRESS_CANCEL,
    WINDOW_WORK_DONE_PROGRESS_CREATE,
    PROGRESS,
)
from lsprotocol.types import (
    CodeLens,
    CodeLensParams,
    CodeLensOptions,
    ProgressParams,
    TextDocumentIdentifier,
    WorkDoneProgressBegin,
    WorkDoneProgressEnd,
    WorkDoneProgressReport,
    WorkDoneProgressCancelParams,
    WorkDoneProgressCreateParams,
)
from ..conftest import ClientServer
from pygls import IS_PYODIDE
from pygls.progress import Progress
from pygls.lsp.server import LanguageServer


class ConfiguredLS(ClientServer):
    def __init__(self):
        super().__init__()
        self.client.notifications: List[ProgressParams] = []
        self.client.method_calls: List[WorkDoneProgressCreateParams] = []

        @self.server.feature(
            TEXT_DOCUMENT_CODE_LENS,
            CodeLensOptions(resolve_provider=False, work_done_progress=True),
        )
        async def f1(params: CodeLensParams) -> Optional[List[CodeLens]]:
            if "client_initiated_token" in params.text_document.uri:
                token = params.work_done_token
            else:
                assert "server_initiated_token" in params.text_document.uri
                token = params.text_document.uri[len("file://") :]
                if "async" in params.text_document.uri:
                    await self.server.work_done_progress.create_async(token)
                else:
                    f = self.server.work_done_progress.create(token)
                    await asyncio.sleep(0.1)
                    f.result()

            assert token
            self.server.protocol.progress.begin(
                token,
                WorkDoneProgressBegin(kind="begin", title="starting", percentage=0),
            )
            await asyncio.sleep(0.1)
            if self.server.protocol.progress.tokens[token].cancelled():
                self.server.protocol.progress.end(
                    token, WorkDoneProgressEnd(kind="end", message="cancelled")
                )
            else:
                self.server.protocol.progress.report(
                    token,
                    WorkDoneProgressReport(
                        kind="report", message="doing", percentage=50
                    ),
                )
                self.server.protocol.progress.end(
                    token, WorkDoneProgressEnd(kind="end", message="done")
                )
            return None

        @self.client.feature(PROGRESS)
        def f2(params):
            self.client.notifications.append(params)
            if params.value["kind"] == "begin" and "cancel" in params.token:
                # client cancels the progress token
                self.client.protocol.notify(
                    WINDOW_WORK_DONE_PROGRESS_CANCEL,
                    WorkDoneProgressCancelParams(token=params.token),
                )

        @self.client.feature(WINDOW_WORK_DONE_PROGRESS_CREATE)
        def f3(params: WorkDoneProgressCreateParams):
            self.client.method_calls.append(params)


@ConfiguredLS.decorate()
def test_capabilities(client_server):
    _, server = client_server
    capabilities = server.server_capabilities

    provider = capabilities.code_lens_provider
    assert provider
    assert provider.work_done_progress


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
@ConfiguredLS.decorate()
async def test_progress_notifications(client_server):
    client, server = client_server
    client.protocol.send_request(
        TEXT_DOCUMENT_CODE_LENS,
        CodeLensParams(
            text_document=TextDocumentIdentifier(uri="file://client_initiated_token"),
            work_done_token="token",
        ),
    ).result()

    assert [notif.value for notif in client.notifications] == [
        {
            "kind": "begin",
            "title": "starting",
            "percentage": 0,
        },
        {
            "kind": "report",
            "message": "doing",
            "percentage": 50,
        },
        {"kind": "end", "message": "done"},
    ]
    assert {notif.token for notif in client.notifications} == {"token"}
    assert server.protocol.progress.tokens == {}


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
@pytest.mark.parametrize("registration", ("sync", "async"))
@ConfiguredLS.decorate()
async def test_server_initiated_progress_notifications(client_server, registration):
    client, server = client_server
    client.protocol.send_request(
        TEXT_DOCUMENT_CODE_LENS,
        CodeLensParams(
            text_document=TextDocumentIdentifier(
                uri=f"file://server_initiated_token_{registration}"
            ),
            work_done_token="token",
        ),
    ).result()

    assert [notif.value for notif in client.notifications] == [
        {
            "kind": "begin",
            "title": "starting",
            "percentage": 0,
        },
        {
            "kind": "report",
            "message": "doing",
            "percentage": 50,
        },
        {"kind": "end", "message": "done"},
    ]
    assert {notif.token for notif in client.notifications} == {
        f"server_initiated_token_{registration}"
    }
    assert [mc.token for mc in client.method_calls] == [
        f"server_initiated_token_{registration}"
    ]
    assert server.protocol.progress.tokens == {}


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
@ConfiguredLS.decorate()
def test_progress_cancel_notifications(client_server):
    client, server = client_server
    client.protocol.send_request(
        TEXT_DOCUMENT_CODE_LENS,
        CodeLensParams(
            text_document=TextDocumentIdentifier(uri="file://client_initiated_token"),
            work_done_token="token_with_cancellation",
        ),
    ).result()
    assert [notif.value for notif in client.notifications] == [
        {
            "kind": "begin",
            "title": "starting",
            "percentage": 0,
        },
        {"kind": "end", "message": "cancelled"},
    ]
    assert {notif.token for notif in client.notifications} == {
        "token_with_cancellation"
    }
    assert server.protocol.progress.tokens == {}


@pytest.mark.skipif(IS_PYODIDE, reason="threads are not available in pyodide.")
@pytest.mark.parametrize("registration", ("sync", "async"))
@ConfiguredLS.decorate()
def test_server_initiated_progress_progress_cancel_notifications(
    client_server, registration
):
    client, server = client_server
    client.protocol.send_request(
        TEXT_DOCUMENT_CODE_LENS,
        CodeLensParams(
            text_document=TextDocumentIdentifier(
                uri=f"file://server_initiated_token_{registration}_with_cancellation"
            ),
        ),
    ).result()

    assert [notif.value for notif in client.notifications] == [
        {
            "kind": "begin",
            "title": "starting",
            "percentage": 0,
        },
        {"kind": "end", "message": "cancelled"},
    ]
    assert server.protocol.progress.tokens == {}


@pytest.mark.parametrize("token", (1, "token"))
@pytest.mark.parametrize("cancelled", (False, True))
def test_end_releases_only_the_finished_token(token, cancelled):
    protocol = Mock()
    progress = Progress(protocol)
    progress.begin(token, WorkDoneProgressBegin(title="finished"))
    progress.begin("active", WorkDoneProgressBegin(title="still running"))
    finished = progress.tokens[token]
    active = progress.tokens["active"]
    if cancelled:
        finished.cancel()

    value = WorkDoneProgressEnd(message="done")
    progress.end(token, value)

    assert progress.tokens == {"active": active}
    assert finished.cancelled() is cancelled
    assert not active.done()
    protocol.notify.assert_called_with(
        PROGRESS, ProgressParams(token=token, value=value)
    )


def test_end_releases_token_before_notifying():
    server = LanguageServer("progress-test", "v1")
    progress = server.work_done_progress
    server.protocol.notify = Mock()
    progress.begin("token", WorkDoneProgressBegin(title="finished"))
    finished = progress.tokens["token"]

    # A late cancellation received while publishing the end notification must
    # not reach the finished operation's cancellation future.
    server.protocol.notify.side_effect = lambda *_: list(
        server.protocol.lsp_work_done_progress_cancel(
            WorkDoneProgressCancelParams(token="token")
        )
    )
    progress.end("token", WorkDoneProgressEnd())

    assert progress.tokens == {}
    assert not finished.cancelled()


def test_end_releases_token_if_notification_fails():
    protocol = Mock()
    progress = Progress(protocol)
    progress.begin("token", WorkDoneProgressBegin(title="finished"))
    protocol.notify.side_effect = BrokenPipeError

    with pytest.raises(BrokenPipeError):
        progress.end("token", WorkDoneProgressEnd())

    assert progress.tokens == {}


def test_end_unknown_token_still_notifies():
    protocol = Mock()
    progress = Progress(protocol)
    value = WorkDoneProgressEnd(message="done")

    progress.end("unknown", value)

    assert progress.tokens == {}
    protocol.notify.assert_called_once_with(
        PROGRESS, ProgressParams(token="unknown", value=value)
    )


def test_finished_operations_do_not_accumulate_tokens():
    progress = Progress(Mock())
    progress.begin("active", WorkDoneProgressBegin(title="still running"))
    active = progress.tokens["active"]

    for token in range(100):
        progress.begin(token, WorkDoneProgressBegin(title="finished"))
        progress.end(token, WorkDoneProgressEnd())
        assert progress.tokens == {"active": active}
