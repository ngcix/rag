.PHONY: compile run build build-only install clean help

help:
	@echo "Available targets:"
	@echo "  compile     - Compile Cython extensions in-place (development)"
	@echo "  run         - Run the application"
	@echo "  build       - Full build: compile Cython + build wheel + pip install"
	@echo "  build-only  - Build wheel only (no install)"
	@echo "  install     - Install built wheel via pip"
	@echo "  clean       - Clean all build artifacts (build/, dist/, cython_build/)"
	@echo "  clean-src   - Clean only compiled extensions (.c, .so, .pyd)"
	@echo "  help        - Show this help message"

compile: clean-src
	python setup.py build_ext --inplace

run:
	python src/rag/main.py

build: build-only install

build-only: clean-all
	python buildscript/main.py -c

install:
	python buildscript/main.py -w

clean: clean-all

clean-src:
	python -c "import shutil, glob; [shutil.rmtree(f, ignore_errors=True) for f in glob.glob('src/**/*.c', recursive=True)]; [shutil.rmtree(f, ignore_errors=True) for f in glob.glob('src/**/*.so', recursive=True)]; [shutil.rmtree(f, ignore_errors=True) for f in glob.glob('src/**/*.pyd', recursive=True)]"

clean-all:
	python -c "import shutil; shutil.rmtree('build', ignore_errors=True); shutil.rmtree('dist', ignore_errors=True); shutil.rmtree('cython_build', ignore_errors=True)"
