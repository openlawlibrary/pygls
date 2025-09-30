.PHONY: dist
dist: out/extension.js | $(NPX)
	$(NPX) vsce package

.PHONY: clean
clean:
	-test -d node_modules && rm -r node_modules/
	-test -d out && rm -r out/
	-rm *.vsix

out/extension.js: src/extension.ts node_modules/.installed | $(NPM)
	$(NPM) run compile


node_modules/.installed: package.json package-lock.json | $(NPM)
ifdef CI
	$(NPM) ci
else
	$(NPM) install
endif

include ../../../.devcontainer/tools.mk
