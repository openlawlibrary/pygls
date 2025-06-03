.PHONY: dist
dist: | $(POETRY)
	$(POETRY) install --all-extras
	git describe --tags --abbrev=0
	$(POETRY) build

.PHONY: lint
lint: | $(POETRY)
	$(POETRY) install --all-extras --with dev
	$(POETRY) run poe lint

.PHONY: test
test: | $(POETRY)
	$(POETRY) install --all-extras
	$(POETRY) run poe test

.PHONY: test-pyodide
test-pyodide: dist | $(NPM) $(POETRY)
	$(POETRY) install --with test
	cd tests/pyodide && $(NPM) ci
	$(POETRY) run poe test-pyodide

.PHONY: pygls-playground
pygls-playground: | $(NPM) $(POETRY)
	$(POETRY) install --all-extras
	cd .vscode/extensions/pygls-playground && $(NPM) install --no-save
	cd .vscode/extensions/pygls-playground && $(NPM) run compile

include .devcontainer/tools.mk
