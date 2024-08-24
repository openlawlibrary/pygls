# How To Make A New Release Of PyGLS

1. Update the version number in `pyproject.toml`

    - Try to follow https://semver.org/
    - Commit message title should be something like: `build: v1.3.0`
    - Typically you'll want to make a dedicated PR for the version bump. But if a previous PR has already merged the wanted version bump into main, then a new PR is not necessary.
    - Example PR for a release https://github.com/openlawlibrary/pygls/pull/434
    - Merge the PR

2. Create a Github Release

    - Goto https://github.com/openlawlibrary/pygls/releases/new
    - In the "Choose a tag" dropdown button, type the new version number.
    - Click the "Generate release notes" button.
    - Generating release notes does not require making an actual release, so you may like to copy and paste the output of the release notes to make the above release PR more informative.
    - If it's a pre-release, remember to check the "Set as a pre-release" toggle.
    - Click the green "Publish release button".
    - Once the Github Release Action is complete (see https://github.com/openlawlibrary/pygls/actions), check https://pypi.org/project/pygls/ to verify that the new release is available.

## Notes

-   `CHANGELOG.md` and `CONTRIBUTORS.md` are automatically populated in the Github Release Action.
-   PyPi automatically detects beta and alpha versions from the version string, eg `v1.0.0a`, and prevents them from being the latest version. In other words, they're made publicly available but downstream projects with loose pinning (eg `^1.0.0`) won't automatically install them.
