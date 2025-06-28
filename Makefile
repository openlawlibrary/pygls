.PHONY: dist
dist: | $(UV)
	git describe --tags --abbrev=0
	$(UV) build

.PHONY: lint
lint: | $(UV)
	$(UV) run --all-extras poe lint

.PHONY: test
test: | $(UV)
	$(UV) run --all-extras poe test

.PHONY: test-pyodide
test-pyodide: dist | $(NPM) $(UV)
	$(UV) sync --group test
	cd tests/pyodide && $(NPM) ci
	$(UV) run poe test-pyodide

.PHONY: pygls-playground
pygls-playground: | $(NPM) $(UV)
	$(UV) sync --all-extras
	cd .vscode/extensions/pygls-playground && $(NPM) install --no-save
	cd .vscode/extensions/pygls-playground && $(NPM) run compile

include .devcontainer/tools.mk
