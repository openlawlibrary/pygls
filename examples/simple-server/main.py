from pygls.ls import LanguageServer
from pygls import lsp

ls = LanguageServer()


@ls.feature(lsp.COMPLETION, triggerCharacters=['.'])
def completions(textDocument=None, position=None, **_kwargs):
    return {
        'isIncomplete': False,
        'items': [{'label': 'AAA'}, {'label': 'BBB'}]
    }


@ls.feature(lsp.CODE_LENS)
def lens(doc_uri=None, **_kwargs):
    pass


ls.start_tcp("127.0.0.1", 2087)
