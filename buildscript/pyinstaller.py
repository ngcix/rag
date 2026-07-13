import time
import os
from datetime import timedelta

import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

from config import *


def safe_collect_all(pkg):
    try:
        d, b, h = collect_all(pkg)
        print(f"Collected {pkg}: {len(d)} datas, {len(b)} binaries, {len(h)} hidden")
        return d, b, h
    except Exception as e:
        print(f"Warning: collect_all({pkg}) failed: {e}")
        return [], [], []


def build(project_name, my_modules, packages=None, hidden_imports=None, metadata_packages=None, debug=False):
    """
    Build executable using PyInstaller

    Args:
        project_name: Tên project (default: "rag")
        my_modules: List custom modules need for hidden imports
        packages: List of packages to collect_all (data + binaries + hidden imports)
        hidden_imports: Additional hidden imports
        metadata_packages: List of packages to copy metadata
        debug: Enable debug mode
    """
    if my_modules is None:
        my_modules = []
    if packages is None:
        packages = PYINSTALLER_PACKAGES
    if hidden_imports is None:
        hidden_imports = []
    if metadata_packages is None:
        metadata_packages = PYINSTALLER_METADATA_PACKAGES

    start_time = time.perf_counter()

    datas = []
    binaries = []

    # If you get the error module not found, you MUST add them manually
    all_hidden_imports = PYINSTALLER_HIDDEN_IMPORTS + hidden_imports + my_modules

    for pkg in packages:
        d, b, h = safe_collect_all(pkg)
        datas += d
        binaries += b
        all_hidden_imports += h

    # hidden_imports += collect_submodules("transformers")

    # Build arguments
    args = [
        "./src/rag/main.py",
        "-D",
        f"-n={project_name}",
        "--clean",
        "-y",
        *([f"--copy-metadata={pkg}" for pkg in metadata_packages] if metadata_packages else []),
        *([f"--add-data={src}{os.pathsep}{dest}" for src, dest in datas] if datas else []),
        *([f"--add-binary={src}{os.pathsep}{dest}" for src, dest in binaries] if binaries else []),
        *([f"--hidden-import={hi}" for hi in all_hidden_imports] if all_hidden_imports else []),
        *((["--debug", "imports", "--log-level", "DEBUG"]) if debug else []),
    ]

    print(f"Building {project_name}...")
    PyInstaller.__main__.run(args)

    end_time = time.perf_counter()
    elapsed = timedelta(seconds=int(end_time - start_time))
    print(f"✓ Build finished: {elapsed}")
