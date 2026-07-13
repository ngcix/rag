import os
import sys
import glob
import shutil
import subprocess

import cython_build
import pyinstaller
from config import *


def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        sys.exit(1)


def clean_src():
    """Clean only compiled extensions (.c, .so, .pyd)"""
    print("Cleaning compiled extensions...")
    extensions = ['*.c', '*.so', '*.pyd']
    for ext in extensions:
        files = glob.glob(f"src/rag/**/{ext}", recursive=True)
        for f in files:
            try:
                os.remove(f)
                print(f"Removed: {f}")
            except Exception as e:
                print(f"Error removing {f}: {e}")

def clean_all():
    """Clean all build artifacts (build/, dist/, cython_build/)"""
    print("Cleaning all build artifacts...")
    targets = [BUILD_DIR, "dist", "cython_build"]
    for target in targets:
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            print(f"Removed: {target}")

def main():
    if "-h" in sys.argv:
        print("-c: clean up old cython build output")
        print("-i: run pyinstaller after cython build")
        print("-w: build wheel and install via pip (default)")
        print("-clean-src: clean compiled extensions")
        print("-clean-all: clean all build artifacts")
        sys.exit()

    if "-clean-src" in sys.argv:
        clean_src()
        return

    if "-clean-all" in sys.argv:
        clean_all()
        return

    if "-c" in sys.argv:
        # maintain backward compatibility with -c
        clean_all()

    # Build wheel and install via pip (clean installation)
    wheel_path = cython_build.build_wheel()
    cython_build.pip_uninstall_package()
    cython_build.pip_install_wheel(wheel_path)

    print(f"MY_MODULES: {MY_MODULES}")

    if "-i" in sys.argv:
        pyinstaller.build(PACKAGE_NAME, MY_MODULES, PYINSTALLER_PACKAGES, PYINSTALLER_HIDDEN_IMPORTS, PYINSTALLER_METADATA_PACKAGES)

if __name__ == "__main__":
    main()
