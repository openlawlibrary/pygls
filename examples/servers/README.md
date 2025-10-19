# Example Servers

See the [docs](https://pygls.readthedocs.io/en/latest/pygls/howto/use-the-pygls-playground.html#howto-use-pygls-playground) for instructions on how to run these in VSCode.

| Filename | Works With | Description |
|-|-|-|
| `code_actions.py` | `sums.txt` | Evaluate sums via a code action |
| `code_lens.py` | `sums.txt` | Evaluate sums via a code lens |
| `colors.py` | `colors.txt` | Provides a visual representation of color values and even a color picker in supported clients |
| `formatting.py`| `table.txt`| Implements whole document, selection only and as-you-type formatting for markdown like tables [^1] [^2] |
| `goto.py` | `code.txt` | Implements the various "Goto X" and "Find references" requests in the specification |
| `hover.py` | `dates.txt` | Opens a popup showing the date underneath the cursor in multiple formats |
| `inlay_hints.py` | `sums.txt` | Use inlay hints to show the binary representation of numbers in the file |
| `links.py` | `links.txt` | Implements `textDocument/documentLink` |
| `publish_diagnostics.py` | `sums.txt` | Use "push-model" diagnostics to highlight missing or incorrect answers |
| `pull_diagnostics.py` | `sums.txt` | Use "pull-model" diagnostics to highlight missing or incorrect answers |
| `rename.py` | `code.txt` | Implements symbol renaming |


[^1]: To enable as-you-type formatting, be sure to uncomment the `editor.formatOnType` option in `.vscode/settings.json`

[^2]: This server is enough to demonstrate the bare minimum required to implement these methods be sure to check the contents of the `params` object for all the additional options you shoud be considering!
