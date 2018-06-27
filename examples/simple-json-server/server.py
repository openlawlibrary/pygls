##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
import json
from json import JSONDecodeError

from pygls.ls import LanguageServer
from pygls import lsp

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


@ls.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def text_doc_did_save(ls, textDocument=None, **_kwargs):
    '''
    Validates json file on save
    '''
    doc = ls.workspace.get_document(textDocument['uri'])

    diagnostics = []

    try:
        json.loads(doc.source)
    except JSONDecodeError as err:
        msg = err.msg
        col = err.colno
        line = err.lineno

        diagnostics.append({
            'range':
                {
                    'start': {
                        'line': line - 1,
                        'character': col - 1
                    },
                    'end': {
                        'line': line - 1,
                        'character': col
                    }
                },
            'message': msg,
            'severity': lsp.DiagnosticSeverity.Error,
            'source': type(ls).__name__
        })

    ls.workspace.publish_diagnostics(textDocument['uri'], diagnostics)


@ls.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def text_doc_did_open(ls, textDocument=None, **_kwargs):
    '''
    Logs to output channel
    '''
    ls.workspace.show_message_log("OPENED", msg_type=lsp.MessageType.Info)


@ls.feature(lsp.TEXT_DOCUMENT_DID_CLOSE)
def text_doc_did_close(ls, textDocument=None, **_kwargs):
    '''
    Sends notification
    '''
    ls.workspace.show_message("CLOSED")


ls.start_tcp("127.0.0.1", 2087)
