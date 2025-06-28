## Description (e.g. "Related to ...", etc.)

_Please replace this description with a concise description of this Pull Request._

## Code review checklist (for code reviewer to complete)

- [ ] Pull request represents a single change (i.e. not fixing disparate/unrelated things in a single PR)
- [ ] Title summarizes what is changing
- [ ] Commit messages are meaningful (see [this][commit messages] for details)
- [ ] Tests have been included and/or updated, as appropriate
- [ ] Docstrings have been included and/or updated, as appropriate
- [ ] Standalone docs have been updated accordingly

## Automated linters

You can run the lints that are run on CI locally with:
```sh
uv run --all-extras poe lint
```

[commit messages]: https://conventionalcommits.org/
