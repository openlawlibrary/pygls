from typing import Optional, Union

from pygls.types.common import NumType

ProgressToken = Union[int, str]


class WorkDoneProgressBegin:
    def __init__(self,
                 title: str,
                 cancellable: Optional[bool] = False,
                 message: Optional[str] = None,
                 percentage: Optional[NumType] = None):
        self.kind = 'begin'
        self.title = title
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage


class WorkDoneProgressReport:
    def __init__(self,
                 cancellable: Optional[bool] = False,
                 message: Optional[str] = None,
                 percentage: Optional[NumType] = None):
        self.kind = 'report'
        self.cancellable = cancellable
        self.message = message
        self.percentage = percentage


class WorkDoneProgressEnd:
    def __init__(self, message: Optional[str] = None):
        self.kind = 'end'
        self.message = message


class WorkDoneProgressParams:
    def __init__(self, work_done_token: Optional[bool] = None):
        self.workDoneToken = work_done_token


class WorkDoneProgressOptions:
    def __init__(self, work_done_progress: Optional[ProgressToken] = None):
        self.workDoneProgress = work_done_progress


class PartialResultParams:
    def __init__(self, partial_result_token: Optional[ProgressToken] = None):
        self.partialResultToken = partial_result_token
