.PHONY: help exe Makefile

help:
	@echo "Try one of the following targets as 'make <target>':"
	@echo "install server clean debug debug-py"

install:
	npm install

server:
	python -m nuitka ./json_server.py --output-dir=./build --standalone --follow-imports --show-progress
	mv ./build/json_server.dist ./dist/json_server

clean:
	rm -rf ./build/*
	rm -rf ./dist/*
	mkdir -p ./dist/json_server

debug:
	./dist/json_server/json_server --tcp --port=2087

debug-py:
	python ./json_server.py --tcp --port=2087