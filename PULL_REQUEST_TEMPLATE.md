## Description (e.g. "Related to ...", etc.)

_Please replace this description with a concise description of this Pull Request._

## LLM Usage

LLM usage is welcomed within reason. Just be considerate of the other humans using and maintaining this project. The only hard rule is that LLM usage must be stated in the PR, Issue, and/or commit message.

## Automated linters

You can run the lints that are run on CI locally with:

```sh
uv run --all-extras poe lint
```

[commit messages]: https://conventionalcommits.org/

## Code review checklist (for code reviewer to complete)

- [ ] Pull request represents a single change (i.e. not fixing disparate/unrelated things in a single PR)
- [ ] Title summarizes what is changing
- [ ] Commit messages are meaningful (see [this][commit messages] for details)
- [ ] Tests have been included and/or updated, as appropriate
- [ ] Docstrings have been included and/or updated, as appropriate
- [ ] Standalone docs have been updated accordingly
