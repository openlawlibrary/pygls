## Description (e.g. "Related to ...", etc.)

_Please replace this description with a concise description of this Pull Request._

## LLM Usage

LLM usage is accepted within reason. The rules are:

- All interactions must be driven by a human. PRs and Issues can neither be submitted by, nor predominantly created by, LLMs.
- LLM usage must be disclosed. This must be done both in PR description bodies and commit messges. "Co-authored by <LLM>" commits are permitted.

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
