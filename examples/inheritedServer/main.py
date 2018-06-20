from pygls.ls import LanguageServer
from pygls import lsp


class MyLanguageServer(LanguageServer):

    def __init__(self):
        super(MyLanguageServer, self).__init__()

    def get_completions(self):
        return [
            {
                'label': 'MyLS1'
            },
            {
                'label': 'MyLS2'
            },
            {
                'label': 'MyLS3'
            }
        ]


ls = MyLanguageServer()


@ls.register(lsp.COMPLETION, triggerCharacters=['.'])
def completions(ls, textDocument=None, position=None, **_kwargs):
    '''
        First argument `ls` is optional and, in this case, it is instance of
        `MyLanguageServer` class
    '''
    return {
        'isIncomplete': False,
        'items': ls.get_completions()
    }


@ls.register(lsp.REGISTER_COMMAND, name='custom.Command')
def custom_command(ls, params):
    '''
        Commands are registered with required `name` argument
    '''
    ls.workspace.show_message('Command `custom.Command` executed')


@ls.register(lsp.TEXT_DOCUMENT_DID_OPEN)
def doc_did_open(ls, textDocument):
    '''
        Do additional stuff here... EG: Lint document
    '''
    # Document is already in our workspace
    doc = ls.workspace.get_document(textDocument['uri'])

    pass


ls.start_tcp("127.0.0.1", 2087)
