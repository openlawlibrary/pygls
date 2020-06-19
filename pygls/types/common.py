import enum
import sys
from typing import Any, Callable, List, Optional, TypeVar, Union

NumType = Union[int, float]
T = TypeVar('T')
ProgressToken = Union[int, str]

ConfigCallbackType = Optional[Callable[[List[Any]], None]]
DocumentChangesType = Union[List['TextDocumentEdit'],
                            'TextDocumentEdit',
                            'CreateFile', 'RenameFile', 'DeleteFile']
DocumentSelectorType = List['DocumentFilter']


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


class CodeActionKind(str, enum.Enum):
    QuickFix = 'quickfix'
    Refactor = 'refactor'
    RefactorExtract = 'refactor.extract'
    RefactorInline = 'refactor.inline'
    RefactorRewrite = 'refactor.rewrite'
    Source = 'source'
    SourceOrganizeImports = 'source.organizeImports'


class CompletionItemKind(enum.IntEnum):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18


class CompletionItemTag(enum.IntEnum):
    Deprecated = 1


class CompletionTriggerKind(enum.IntEnum):
    Invoked = 1
    TriggerCharacter = 2
    TriggerForIncompleteCompletions = 3


class DiagnosticSeverity(enum.IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class DiagnosticTag(enum.IntEnum):
    Unnecessary = 1
    Deprecated = 2


class DocumentHighlightKind(enum.IntEnum):
    Text = 1
    Read = 2
    Write = 3


class FailureHandlingKind(str, enum.Enum):
    Abort = 'abort'
    Transactional = 'transactional'
    TextOnlyTransactional = 'textOnlyTransactional'
    Undo = 'undo'


class FileChangeType(enum.IntEnum):
    Created = 1
    Changed = 2
    Deleted = 3


class FoldingRangeKind(str, enum.Enum):
    Comment = 'comment'
    Imports = 'imports'
    Region = 'region'


class InsertTextFormat(enum.IntEnum):
    PlainText = 1
    Snippet = 2


class MarkupKind(str, enum.Enum):
    PlainText = 'plaintext'
    Markdown = 'markdown'


class MessageType(enum.IntEnum):
    Error = 1
    Warning = 2
    Info = 3
    Log = 4


class ResourceOperationKind(str, enum.Enum):
    Create = 'create'
    Rename = 'rename'
    Delete = 'delete'


class SymbolKind(enum.IntEnum):
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18
    Object = 19
    Key = 20
    Null = 21
    EnumMember = 22
    Struct = 23
    Event = 24
    Operator = 25
    TypeParameter = 26


class TextDocumentSaveReason(enum.IntEnum):
    Manual = 1
    AfterDelay = 2
    FocusOut = 3


class TextDocumentSyncKind(enum.IntEnum):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


class Trace(str, enum.Enum):
    Off = 'off'
    Messages = 'messages'
    Verbose = 'verbose'


if sys.version_info >= (3, 6):
    class WatchKind(enum.IntFlag):
        Create = 1
        Change = 2
        Delete = 4
    _WatchKindType = WatchKind
else:
    # python 3.5 does not have enum.IntFlag
    class WatchKind:
        Create = 1
        Change = 2
        Delete = 4
    _WatchKindType = int
