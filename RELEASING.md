# Releasing a new version of Pygls

Pygls is hosted as a package at https://pypi.org/project/pygls

Releases follow https://keepachangelog.com/en/1.0.0 and https://semver.org/spec/v2.0.0.html

Release notes are kept in CHANGELOG.md

## Steps to release

Update version in `pyproject.toml`

```sh
poetry build
poetry publish --username "$PYPI_USERNAME" --password "$PYPI_PASSWORD"
```
