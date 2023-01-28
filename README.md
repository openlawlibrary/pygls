[![PyPI Version](https://img.shields.io/pypi/v/pygls.svg)](https://pypi.org/project/pygls/) ![!pyversions](https://img.shields.io/pypi/pyversions/pygls.svg) ![license](https://img.shields.io/pypi/l/pygls.svg) [![Documentation Status](https://img.shields.io/badge/docs-latest-green.svg)](https://pygls.readthedocs.io/en/latest/)

# pygls: The Generic Language Server Framework

_pygls_ (pronounced like "pie glass") is a pythonic generic implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/specification) for use as a foundation for writing your own [Language Servers](https://langserver.org/) in just a few lines of code.

## Quickstart
```python
from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    CompletionItem,
    CompletionList,
    CompletionParams,
)

server = LanguageServer("example-server", "v0.1")

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams):
    items = []
    document = server.workspace.get_document(params.text_document.uri)
    current_line = document.lines[params.position.line].strip()
    if current_line.endswith("hello."):
        items = [
            CompletionItem(label="world"),
            CompletionItem(label="friend"),
        ]
    return CompletionList(is_incomplete=False, items=items)

server.start_io()
```

Which might look something like this when you trigger autocompletion in your editor:

![completions](https://raw.githubusercontent.com/openlawlibrary/pygls/master/docs/assets/hello-world-completion.png)

## Docs and Tutorial

The full documentation and a tutorial are available at <https://pygls.readthedocs.io/en/latest/>.

## Projects based on _pygls_

We keep a table of all known _pygls_ [implementations](https://github.com/openlawlibrary/pygls/blob/master/Implementations.md). Please submit a Pull Request with your own or any that you find are missing.

## Alternatives

The main alternative to _pygls_ is Microsoft's [NodeJS-based Generic Language Server Framework](https://github.com/microsoft/vscode-languageserver-node). Being from Microsoft it is focussed on extending VSCode, although in theory it could be used to support any editor. So this is where pygls might be a better choice if you want to support more editors, as pygls is not focussed around VSCode.

There are also other Language Servers with "general" in their descriptons, or at least intentions. They are however only general in the sense of having powerful _configuration_. They achieve generality in so much as configuration is able to, as opposed to what programming (in _pygls'_ case) can achieve.
  * https://github.com/iamcco/diagnostic-languageserver
  * https://github.com/mattn/efm-langserver
  * https://github.com/jose-elias-alvarez/null-ls.nvim (Neovim only)

## Contributing

Your contributions to _pygls_ are most welcome ❤️ Please review the [Contributing](https://github.com/openlawlibrary/pygls/blob/master/CONTRIBUTING.md) and [Code of Conduct](https://github.com/openlawlibrary/pygls/blob/master/CODE_OF_CONDUCT.md) documents for how to get started.

## Donating

[Open Law Library](http://www.openlawlib.org/) is a 501(c)(3) tax exempt organization. Help us maintain our open source projects and open the law to all with [sponsorship](https://github.com/sponsors/openlawlibrary).

### Supporters

We would like to give special thanks to the following supporters:
* [mpourmpoulis](https://github.com/mpourmpoulis)

## License

Apache-2.0
