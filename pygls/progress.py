import asyncio
from concurrent.futures import Future
from typing import Dict

from pygls.lsp.methods import (PROGRESS_NOTIFICATION, WINDOW_WORK_DONE_PROGRESS_CANCEL,
                               WINDOW_WORK_DONE_PROGRESS_CREATE)
from pygls.lsp.types.basic_structures import (ProgressParams, ProgressToken, WorkDoneProgressBegin,
                                              WorkDoneProgressEnd, WorkDoneProgressReport)
from pygls.lsp.types.window import WorkDoneProgressCancelParams, WorkDoneProgressCreateParams
from pygls.protocol import LanguageServerProtocol


class Progress:

    def __init__(self, lsp: LanguageServerProtocol) -> None:
        self._lsp = lsp

        self.tokens: Dict[ProgressToken, None] = {}

    def create(self, token: ProgressToken, callback=None) -> Future:
        if token in self.tokens:
            raise Exception("Token is already registered!")  # TODO

        def on_created(*args, **kwargs):
            self.tokens[token] = None
            if callback:
                callback(*args, **kwargs)

        return self._lsp.send_request(
            WINDOW_WORK_DONE_PROGRESS_CREATE,
            WorkDoneProgressCreateParams(token=token),
            on_created,
        )

    async def create_async(self, token: ProgressToken) -> asyncio.Future:
        result = await self._lsp.send_request_async(
            WINDOW_WORK_DONE_PROGRESS_CREATE,
            WorkDoneProgressCreateParams(token=token),
        )
        self.tokens[token] = None

        return result

    def cancel(self, token: ProgressToken, callback=None) -> Future:
        def on_canceled(*args, **kwargs):
            del self.tokens[token]

            if callback:
                callback(*args, **kwargs)

        return self._lsp.send_request(
            WINDOW_WORK_DONE_PROGRESS_CANCEL,
            WorkDoneProgressCancelParams(token=token),
            callback=on_canceled,
        )

    def cancel_async(self, token: ProgressToken) -> asyncio.Future:
        return asyncio.wrap_future(self.cancel(token))

    def begin(self, token: ProgressToken, value: WorkDoneProgressBegin) -> None:
        return self._lsp.notify(
            PROGRESS_NOTIFICATION,
            ProgressParams(
                token=token,
                value=value
            )
        )

    def report(self, token: ProgressToken, value: WorkDoneProgressReport) -> None:
        self._lsp.notify(PROGRESS_NOTIFICATION, ProgressParams(token=token, value=value))

    def end(self, token: ProgressToken, value: WorkDoneProgressEnd) -> None:
        self._lsp.notify(PROGRESS_NOTIFICATION, ProgressParams(token=token, value=value))
