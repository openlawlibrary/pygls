ARCH ?= $(shell arch)
BIN ?= $(HOME)/.local/bin

ifeq ($(strip $(ARCH)),)
$(error Unable to determine platform architecture)
endif

NODE_VERSION := 20.19.3
UV_VERSION := 0.7.16

UV ?= $(shell command -v uv)
UVX ?= $(shell command -v uvx)

ifeq ($(strip $(UV)),)

UV := $(BIN)/uv
UVX := $(BIN)/uvx

$(UV):
	curl -L --output /tmp/uv.tar.gz https://github.com/astral-sh/uv/releases/download/$(UV_VERSION)/uv-$(ARCH)-unknown-linux-gnu.tar.gz
	tar -xf /tmp/uv.tar.gz -C /tmp
	rm /tmp/uv.tar.gz

	test -d $(BIN) || mkdir -p $(BIN)

	mv /tmp/uv-$(ARCH)-unknown-linux-gnu/uv $@
	mv /tmp/uv-$(ARCH)-unknown-linux-gnu/uvx $(UVX)

	$@ --version
	$(UVX) --version

endif

# Node JS
NPM ?= $(shell command -v npm)
NPX ?= $(shell command -v npx)

ifeq ($(strip $(NPM)),)

NPM := $(BIN)/npm
NPX := $(BIN)/npx
NODE := $(BIN)/node
NODE_DIR := $(HOME)/.local/node

$(NPM):
	curl -L --output /tmp/node.tar.xz https://nodejs.org/dist/v$(NODE_VERSION)/node-v$(NODE_VERSION)-linux-x64.tar.xz
	tar -xJf /tmp/node.tar.xz -C /tmp
	rm /tmp/node.tar.xz

	[ -d $(NODE_DIR) ] || mkdir -p $(NODE_DIR)
	mv /tmp/node-v$(NODE_VERSION)-linux-x64/* $(NODE_DIR)

	[ -d $(BIN) ] || mkdir -p $(BIN)
	ln -s $(NODE_DIR)/bin/node $(NODE)
	ln -s $(NODE_DIR)/bin/npm $(NPM)
	ln -s $(NODE_DIR)/bin/npx $(NPX)

	$(NODE) --version
	PATH=$(BIN) $(NPM) --version
	PATH=$(BIN) $(NPX) --version

endif

# One command to bootstrap all tools and check their versions
.PHONY: tools
tools: $(UV) $(NPM) $(NPX)
	for prog in $^ ; do echo -n "$${prog}\t" ; PATH=$(BIN) $${prog} --version; done
