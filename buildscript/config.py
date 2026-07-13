import os, re


# Configuration for the project
PACKAGE_NAME = "rag"
VERSION = "0.1"
ENTRY_POINT = "src/rag/main.py"

CYTHON_DIRECTIVES = {
    "language_level": "3",
    "embedsignature": True,
}

FILE_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.abspath(os.path.dirname(FILE_DIR))
SRC_DIR = os.path.join(BASE_DIR, "src")
BUILD_DIR = os.path.join(BASE_DIR, "build")
CYTHON_DIR = "build/cython"
LIB_DIR_RE = re.compile(r".*lib\..*-cpython-([0-9]*)")


# PyInstaller configurations
PYINSTALLER_PACKAGES = [
    # "torch",
    # "transformers",
]

PYINSTALLER_HIDDEN_IMPORTS = [
    # "transformers.integrations",
    # "transformers.utils",
]

PYINSTALLER_METADATA_PACKAGES = [
    # "transformers",
    # "torch",
]
