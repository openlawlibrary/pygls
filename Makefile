PY ?= 3.13

.PHONY: dist
dist: | $(UV)
	git describe --tags --abbrev=0
	$(UV) build

.PHONY: clean-docs
clean-docs:
	rm -r docs/build

.PHONY: docs
docs: docs/requirements.txt | $(UV)
	$(UV) run --group docs sphinx-build -M html docs/source docs/build

docs/requirements.txt: uv.lock | $(UV)
	$(UV) export --format requirements.txt --all-extras --no-emit-project --no-default-groups --group docs --output-file $@

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
	cd .vscode/extensions/pygls-playground && make dist

include .devcontainer/tools.mk
