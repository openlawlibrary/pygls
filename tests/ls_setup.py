##########################################################################
# Copyright (c) Open Law Library. All rights reserved.                   #
# See ThirdPartyNotices.txt in the project root for license information. #
##########################################################################
from pygls import lsp

from tests import TRIGGER_CHARS, COMMANDS


def setup_ls_features(ls):

    # Workspace
    @ls.feature(lsp.WORKSPACE_SYMBOL)
    def workspace_symbol():
        return True

    # Language Features
    @ls.feature(lsp.COMPLETION, triggerCharacters=TRIGGER_CHARS)
    def completions(ls, textDocument=None, position=None, **_kwargs):
        return True

    @ls.feature(lsp.COMPLETION_ITEM_RESOLVE)
    def completion_item_resolve(ls, completionItem=None, **_kwargs):
        return True

    @ls.feature(lsp.HOVER)
    def hover(ls, textDocument=None, position=None, **_kwargs):
        return True

    @ls.feature(lsp.SIGNATURE_HELP, triggerCharacters=TRIGGER_CHARS)
    def signature_help():
        return True

    @ls.feature(lsp.DEFINITION)
    def definition():
        return True

    @ls.feature(lsp.TYPE_DEFINITION)
    def type_definition():
        return True

    @ls.feature(lsp.IMPLEMENTATION)
    def implementation():
        return True

    @ls.feature(lsp.REFERENCES)
    def references():
        return True

    @ls.feature(lsp.DOCUMENT_HIGHLIGHT)
    def document_highlight():
        return True

    @ls.feature(lsp.DOCUMENT_SYMBOL)
    def document_symbol():
        return True

    @ls.feature(lsp.CODE_ACTION)
    def code_action():
        return True

    @ls.feature(lsp.CODE_LENS)
    def code_lens():
        return True

    @ls.feature(lsp.CODE_LENS_RESOLVE)
    def code_lens_resolve():
        return True

    @ls.feature(lsp.DOCUMENT_LINK)
    def document_link():
        return True

    @ls.feature(lsp.DOCUMENT_LINK_RESOLVE)
    def document_link_resolve():
        return True

    @ls.feature(lsp.COLOR_PRESENTATION)
    def color_presentation():
        return True

    @ls.feature(lsp.FORMATTING)
    def formatting():
        return True

    @ls.feature(lsp.RANGE_FORMATTING)
    def range_formatting():
        return True

    @ls.feature(lsp.ON_TYPE_FORMATTING)
    def on_type_formatting():
        return True

    @ls.feature(lsp.RENAME)
    def rename():
        return True

    # Commands

    @ls.command(COMMANDS[0])
    def command1(ls, args):
        try:
            x = args[0]
            y = args[1]

            return x + y
        except:
            raise Exception("Invalid arguments")

    @ls.command(COMMANDS[1])
    def command2(ls):
        return True
