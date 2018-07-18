##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import json

from json import JSONDecodeError

from pygls import lsp
from pygls.ls import LanguageServer

ls = LanguageServer()


@ls.feature(lsp.COMPLETION, triggerCharacters=[','])
def completions(textDocument=None, position=None, **_kwargs):
    '''
    Returns completion items (dummy)
    '''
    return {
        'isIncomplete': False,
        'items': [{'label': '"'},
                  {'label': '['},
                  {'label': '{'},
                  {'label': '}'},
                  {'label': ']'}]
    }


@ls.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def text_doc_did_close(ls, textDocument=None, **_kwargs):
    '''
    Sends notification
    '''
    ls.workspace.show_message("CLOSED")


@ls.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def text_doc_did_open(ls, textDocument=None, **_kwargs):
    '''
    Logs to output channel
    '''
    ls.workspace.show_message_log("OPENED", msg_type=lsp.MessageType.Info)


@ls.feature(lsp.TEXT_DOCUMENT_DID_CHANGE, lsp.TEXT_DOCUMENT_DID_SAVE)
def validate_json(ls, textDocument=None, **_kwargs):
    '''
    Validates json file on save and on change
    '''
    doc = ls.workspace.get_document(textDocument['uri'])

    diagnostics = []

    try:
        json.loads(doc.source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        d = lsp.Diagnostic(
            lsp.Range(
                lsp.Position(line-1, col-1),
                lsp.Range(line-1, col)
            ),
            msg,
            source=type(ls).__name__
        )

        diagnostics.append(d)

    ls.workspace.publish_diagnostics(textDocument['uri'], diagnostics)


ls.start_tcp("127.0.0.1", 2087)
