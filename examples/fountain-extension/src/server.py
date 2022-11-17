import re
from pygls.server import LanguageServer
from lsprotocol.types import TEXT_DOCUMENT_COMPLETION
from lsprotocol.types import (CompletionItem, CompletionParams, CompletionList, CompletionOptions)

server = LanguageServer("foutain-language-server", "v0.1")

CHARACTER = re.compile(r"^[A-Z][A-Z ]+$", re.MULTILINE)

@server.feature(TEXT_DOCUMENT_COMPLETION, CompletionOptions(trigger_characters=['.']))
def on_completion(ls: LanguageServer, params: CompletionParams) -> CompletionList:
    """Completion suggestions for character names."""

    uri = params.text_document.uri
    doc = ls.workspace.get_document(uri)

    characters = set(CHARACTER.findall(doc.source))

    return CompletionList(
        is_incomplete=False,
        items=[CompletionItem(label=character) for character in characters]
    )
