PY ?= 3.13

.PHONY: dist
dist: | $(UV)
	git describe --tags --abbrev=0
	$(UV) build

.PHONY: lint
lint: | $(UV)
	$(UV) run --all-extras poe lint

.PHONY: test
test: | $(UV)
	$(UV) run --managed-python --python $(PY) --group test --all-extras poe test

.PHONY: test-pyodide
test-pyodide: dist | $(NPM) $(UV)
	cd tests/pyodide && $(NPM) ci
	$(UV) run --managed-python --python $(PY) --group test poe test-pyodide

.PHONY: pygls-playground
pygls-playground: | $(NPM) $(UV)
	$(UV) sync --managed-python --python $(PY) --all-extras
	cd .vscode/extensions/pygls-playground && $(NPM) install --no-save
	cd .vscode/extensions/pygls-playground && $(NPM) run compile

include .devcontainer/tools.mk
