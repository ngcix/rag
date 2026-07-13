.PHONY: setup-env test compile run run-exec build build-only build-exec install clean clean-src clean-all help

help:
	@echo "Available targets:"
	@echo "  setup-env    - Create virtual environment and install dependencies"
	@echo "  test         - Run project tests"
	@echo "  compile      - Compile Cython extensions in-place (development)"
	@echo "  run          - Run the application"
	@echo "  run-exec     - Run the bundled executable"
	@echo "  build        - Full build: compile Cython + build wheel + pip install"
	@echo "  build-only   - Build wheel only (no install)"
	@echo "  build-exec   - Build and run PyInstaller executable"
	@echo "  install      - Install built wheel via pip"
	@echo "  clean        - Clean all build artifacts (build/, dist/, cython_build/)"
	@echo "  clean-src    - Clean only compiled extensions (.c, .so, .pyd)"
	@echo "  help         - Show this help message"

setup-env:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	./venv/bin/pip install pytest

test:
	PYTHONPATH=src pytest tests/

compile: clean-src
	python setup.py build_ext --inplace

run:
	PYTHONPATH=src python -m rag.main

run-exec:
	./dist/rag/rag

build: build-only install

build-only: clean-all
	python buildscript/main.py -c

build-exec:
	python buildscript/main.py -c -i

install:
	python buildscript/main.py -w

clean: clean-all

clean-src:
	python buildscript/main.py -clean-src

clean-all:
	python buildscript/main.py -clean-all
