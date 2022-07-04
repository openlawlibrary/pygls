# Releasing a new version of Pygls

Pygls is hosted as a package at https://pypi.org/project/pygls

Releases follow https://keepachangelog.com/en/1.0.0 and https://semver.org/spec/v2.0.0.html

Release notes are kept in CHANGELOG.md

## Steps to release

  * Install:
      * Python's [build module](https://pypa-build.readthedocs.io/en/latest/) with Pip or your
        OS's package manager
      * [Twine](https://twine.readthedocs.io/en/stable/) for interacting with pypi.org 
  * It's probably best to make a dedicated release branch, but not essential
  * Update CHANGELOG.md
  * Change version in pygls/__init__.py
  * Commit


```sh
# Python's `setuptools` automatically derives the version from the latest Git tag.
# NB. If the latest commit doesn't have a tag, then `setuptools` will add `dev-[hash]` to the version.
git tag v"$(python -c 'from pygls import __version__; print(__version__)')"

# Build the project into the Source and Wheel formats (they go into `./dist`)
python -m build

# Upload to Pypi
# You'll also need, or have access to, the Pygls Pypi org or account. Likely from @dgreisen
twine upload dist/*
```
