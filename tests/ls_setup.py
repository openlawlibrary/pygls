from pygls import lsp

from tests import TRIGGER_CHARS, COMMANDS


def setup_ls_features(ls):

    # Workspace
    @ls.register(lsp.WORKSPACE_SYMBOL)
    def workspace_symbol():
        return True

    # Language Features
    @ls.register(lsp.COMPLETION, triggerCharacters=TRIGGER_CHARS)
    def completions(ls, textDocument=None, position=None, **_kwargs):
        return True

    @ls.register(lsp.COMPLETION_ITEM_RESOLVE)
    def completion_item_resolve(ls, completionItem=None, **_kwargs):
        return True

    @ls.register(lsp.HOVER)
    def hover(ls, textDocument=None, position=None, **_kwargs):
        return True

    @ls.register(lsp.SIGNATURE_HELP, triggerCharacters=TRIGGER_CHARS)
    def signature_help():
        return True

    @ls.register(lsp.DEFINITION)
    def definition():
        return True

    @ls.register(lsp.TYPE_DEFINITION)
    def type_definition():
        return True

    @ls.register(lsp.IMPLEMENTATION)
    def implementation():
        return True

    @ls.register(lsp.REFERENCES)
    def references():
        return True

    @ls.register(lsp.DOCUMENT_HIGHLIGHT)
    def document_highlight():
        return True

    @ls.register(lsp.DOCUMENT_SYMBOL)
    def document_symbol():
        return True

    @ls.register(lsp.CODE_ACTION)
    def code_action():
        return True

    @ls.register(lsp.CODE_LENS)
    def code_lens():
        return True

    @ls.register(lsp.CODE_LENS_RESOLVE)
    def code_lens_resolve():
        return True

    @ls.register(lsp.DOCUMENT_LINK)
    def document_link():
        return True

    @ls.register(lsp.DOCUMENT_LINK_RESOLVE)
    def document_link_resolve():
        return True

    @ls.register(lsp.COLOR_PRESENTATION)
    def color_presentation():
        return True

    @ls.register(lsp.FORMATTING)
    def formatting():
        return True

    @ls.register(lsp.RANGE_FORMATTING)
    def range_formatting():
        return True

    @ls.register(lsp.ON_TYPE_FORMATTING)
    def on_type_formatting():
        return True

    @ls.register(lsp.RENAME)
    def rename():
        return True

    # Commands

    @ls.register(lsp.REGISTER_COMMAND, name=COMMANDS[0])
    def command1(ls, args):
        try:
            x = args[0]
            y = args[1]

            return x + y
        except:
            raise Exception("Invalid arguments")

    @ls.register(lsp.REGISTER_COMMAND, name=COMMANDS[1])
    def command2(ls):
        return True
