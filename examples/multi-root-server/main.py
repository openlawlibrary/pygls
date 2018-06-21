from pygls.ls import LanguageServer
from pygls import lsp


class MultiRootServer(LanguageServer):

    def __init__(self):
        super().__init__()

    def text_is_valid(self, text='', first_capital=True):
        '''
            Checks if first letter is capital or not
        '''
        if len(text) > 0 and first_capital:
            if text[0].isupper():
                return True

            diagnostics = []

            diagnostics.append({
                'range':
                    {
                        'start': {
                            'line': 0,
                            'character': 0
                        },
                        'end': {
                            'line': 0,
                            'character': 1
                        }
                    },
                'message': "First letter must be capital",
                'severity': lsp.DiagnosticSeverity.Error
            })

            return False, diagnostics
        else:
            return True, None


ls = MultiRootServer()


@ls.register(lsp.REGISTER_COMMAND, name='custom.Command')
def custom_command(ls, params):
    '''
        Commands are registered with required `name` argument
    '''
    ls.workspace.show_message('Command `custom.Command` executed')


@ls.register(lsp.TEXT_DOCUMENT_DID_OPEN)
def doc_did_open(ls, textDocument):
    '''
        Validate document
    '''
    # Document is already in our workspace
    doc = ls.workspace.get_document(textDocument['uri'])

    def callback(config):
        first_capital = config[0].get('firstCapital', True)

        is_valid, diagnostics = ls.text_is_valid(doc.source, first_capital)

        if not is_valid:
            ls.workspace.publish_diagnostics(
                doc.uri, diagnostics)

    ls.get_configuration({'items': [{'scopeUri': doc.uri}]},
                         callback)


ls.start_tcp("127.0.0.1", 2087)
