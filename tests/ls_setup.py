from pygls import lsp


def setup_ls_features(ls):

    # Language Features
    @ls.register(lsp.COMPLETION)
    def completions(ls, textDocument=None, position=None, **_kwargs):
        return {
            'textDocument': textDocument,
            'position': position
        }

    @ls.register(lsp.COMPLETION_ITEM_RESOLVE)
    def completion_item_resolve(ls, completionItem=None, **_kwargs):
        return {
            'completionItem': completionItem
        }

    @ls.register(lsp.HOVER)
    def hover(ls, textDocument=None, position=None, **_kwargs):
        return {
            'textDocument': textDocument,
            'position': position
        }

    @ls.register(lsp.SIGNATURE_HELP)
    def signature_help():
        pass

    @ls.register(lsp.DEFINITION)
    def definition():
        pass

    @ls.register(lsp.TYPE_DEFINITION)
    def type_definition():
        pass

    @ls.register(lsp.IMPLEMENTATION)
    def implementation():
        pass

    @ls.register(lsp.REFERENCES)
    def references():
        pass

    @ls.register(lsp.DOCUMENT_HIGHLIGHT)
    def document_highlight():
        pass

    @ls.register(lsp.DOCUMENT_SYMBOL)
    def document_symbol():
        pass

    @ls.register(lsp.CODE_ACTION)
    def code_action():
        pass

    @ls.register(lsp.CODE_LENS)
    def code_lens():
        pass

    @ls.register(lsp.CODE_LENS_RESOLVE)
    def code_lens_resolve():
        pass

    @ls.register(lsp.DOCUMENT_LINK)
    def document_link():
        pass

    @ls.register(lsp.DOCUMENT_LINK_RESOLVE)
    def document_link_resolve():
        pass

    @ls.register(lsp.COLOR_PRESENTATION)
    def color_presentation():
        pass

    @ls.register(lsp.FORMATTING)
    def formatting():
        pass

    @ls.register(lsp.RANGE_FORMATTING)
    def range_formatting():
        pass

    @ls.register(lsp.ON_TYPE_FORMATTING)
    def on_type_formatting():
        pass

    @ls.register(lsp.RENAME)
    def rename():
        pass
