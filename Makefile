.PHONY: setup-env test compile run run-exec build build-only build-exec install clean clean-exec clean-src help

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
	@echo "  clean        - Nuclear clean: remove everything, uninstall package"
	@echo "  clean-exec   - Light clean: remove only build output and dist"
	@echo "  clean-src    - Clean only compiled extensions (.c, .so, .pyd)"
	@echo "  help         - Show this help message"

setup-env:
	python3 -m venv .venv
	./.venv/bin/pip install --upgrade pip
	./.venv/bin/pip install .
	./.venv/bin/pip install pytest

test:
	PYTHONPATH=src pytest tests/

compile: clean-src
	python setup.py build_ext --inplace

run:
	PYTHONPATH=src python -m rag

run-exec:
	./dist/rag/rag

build: build-only install

build-only: clean
	python buildscript/main.py -c

build-exec:
	python buildscript/main.py -c -i

install:
	python buildscript/main.py -w

clean:
	python buildscript/main.py -clean-all

clean-exec:
	python buildscript/main.py -clean-exec

clean-src:
	python buildscript/main.py -clean-src
