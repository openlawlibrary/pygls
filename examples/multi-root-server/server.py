from pygls.ls import LanguageServer
from pygls import lsp


class MultiRootServer(LanguageServer):

    def __init__(self):
        super().__init__()

    def text_is_valid(self, text='', max_text_len=10):
        '''
            Checks length of the text. Default is 10.
        '''
        diagnostics = []

        if len(text) > max_text_len:
            diagnostics.append({
                'range':
                    {
                        'start': {
                            'line': 0,
                            'character': 0
                        },
                        'end': {
                            'line': 0,
                            'character': max_text_len
                        }
                    },
                'message': f"Max number of characters is {max_text_len}",
                'severity': lsp.DiagnosticSeverity.Error
            })

        return diagnostics


ls = MultiRootServer()


@ls.command('custom.Command')
def custom_command(ls, params):
    '''
        Commands are registered with required `name` argument
    '''
    ls.workspace.show_message('Command `custom.Command` executed')


@ls.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def doc_did_change(ls, contentChanges=None, textDocument=None, **_kwargs):
    '''
        Validate document
    '''
    # Document is already in our workspace
    doc = ls.workspace.get_document(textDocument['uri'])

    def callback(config):
        max_text_len = config[0].get('maxTextLength', 10)

        diagnostics = ls.text_is_valid(doc.source, max_text_len)

        ls.workspace.publish_diagnostics(
            doc.uri, diagnostics)

    ls.get_configuration({'items': [{'scopeUri': doc.uri}]},
                         callback)


ls.start_tcp("127.0.0.1", 2087)
