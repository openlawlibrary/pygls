from pygls.ls import LanguageServer
from pygls import lsp


class MyLanguageServer(LanguageServer):
    def __init__(self):
        super(MyLanguageServer, self).__init__()
        '''
        Add custom fields
        '''


ls = MyLanguageServer()


@ls.register(lsp.COMPLETION, triggerCharacters=['.'])
def completions(textDocument=None, position=None, **_kwargs):
    return {
        'isIncomplete': False,
        'items': [{'label': 'AAA'}, {'label': 'BBB'}]
    }


@ls.register(lsp.CODE_LENS)
def lens(doc_uri=None, **_kwargs):
    pass


ls.start_tcp("127.0.0.1", 2087)
