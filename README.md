# _pygls_

[![PyPI Version](https://img.shields.io/pypi/v/pygls.svg)](https://pypi.org/project/pygls/) [![Build Status](https://dev.azure.com/openlawlibrary/pygls/_apis/build/status/openlawlibrary.pygls?branchName=master)](https://dev.azure.com/openlawlibrary/pygls/_build/latest?definitionId=2&branchName=master) ![!pyversions](https://img.shields.io/pypi/pyversions/pygls.svg) ![license](https://img.shields.io/pypi/l/pygls.svg) [![Documentation Status](https://img.shields.io/badge/docs-latest-green.svg)](https://pygls.readthedocs.io/en/latest/)

_pygls_ (pronounced like "pie glass") is a pythonic generic implementation of the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/specification) for use as a foundation for writing language servers using Python (e.g. Python, XML, etc.). It allows you to write your own [language server](https://langserver.org/) in just a few lines of code.

## Quick Intro

> **_IMPORTANT NOTE:_**
>
> In order to support type-checking, we added `pydantic` library which requires passing keyword arguments when creating [LSP models](https://github.com/openlawlibrary/pygls/blob/master/pygls/lsp/methods.py).

Here's how to create a server and register a code completion feature:

```python
from pygls.features import COMPLETION
from pygls.server import LanguageServer
from pygls.types import CompletionItem, CompletionList, CompletionOptions, CompletionParams

server = LanguageServer()

@server.feature(COMPLETION, CompletionOptions(trigger_characters=[',']))
def completions(params: CompletionParams):
    """Returns completion items."""
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(label='"'),
            CompletionItem(label='['),
            CompletionItem(label=']'),
            CompletionItem(label='{'),
            CompletionItem(label='}'),
        ]
    )

server.start_tcp('localhost', 8080)
```

Show completion list on the client:

![completions](https://raw.githubusercontent.com/openlawlibrary/pygls/master/assets/img/readme/completion-list.png)

## Docs and Tutorial

The full documentation and a tutorial is available at <https://pygls.readthedocs.io/en/latest/>.

## Let Us Know How You Are Using _pygls_

Submit a Pull Request (PR) with your information against the [implementations](https://github.com/openlawlibrary/pygls/blob/master/Implementations.md) document.

## License

Apache-2.0

## Contributing

Your contributions to _pygls_ are welcome! Please review the _[Contributing](https://github.com/openlawlibrary/pygls/blob/master/CONTRIBUTING.md)_ and _[Code of Conduct](https://github.com/openlawlibrary/pygls/blob/master/CODE_OF_CONDUCT.md)_ documents for how to get started.

## Donation

[Open Law Library](http://www.openlawlib.org/) is a 501(c)(3) tax exempt organization.Help us maintain our open source projects and open the law to all with a [donation](https://donorbox.org/open-law-library).
