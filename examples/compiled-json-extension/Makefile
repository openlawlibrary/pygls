.PHONY: help exe Makefile

help:
	@echo "Try one of the following targets as 'make <target>':"
	@echo "server clean"

install:
	npm install

exe:
	python -m nuitka ./json_server.py --output-dir=./build --standalone --follow-imports --show-progress
	mv ./build/json_server.dist ./dist/json_server

clean:
	rm -rf ./build/*
	rm -rf ./dist/*
	mkdir -p ./dist/json_server
