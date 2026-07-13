import os
import sys
import glob
import shutil
import subprocess

import cython_build
import pyinstaller
import config


def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        sys.exit(1)


def clean_src():
    """Clean only compiled extensions (.c, .so, .pyd) and pycache"""
    print("Cleaning compiled extensions and pycache in src...")
    extensions = ['*.c', '*.so', '*.pyd']
    for ext in extensions:
        files = glob.glob(f"src/**/{ext}", recursive=True)
        for f in files:
            try:
                os.remove(f)
                print(f"Removed: {f}")
            except Exception as e:
                print(f"Error removing {f}: {e}")

    # Remove __pycache__ directories in src
    for path in glob.glob("src/**/__pycache__", recursive=True):
        try:
            shutil.rmtree(path)
            print(f"Removed pycache: {path}")
        except Exception as e:
            print(f"Error removing pycache {path}: {e}")


def clean_exec():
    """Clean only basic build output and dist"""
    print("Cleaning build output and dist...")
    targets = [config.BUILD_DIR, "dist"]
    for target in targets:
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            print(f"Removed: {target}")


def clean_all():
    """Clean all build artifacts, uninstall package and remove all pycache/egg-info"""
    print("Performing full cleanup (nuclear option)...")

    # 1. Uninstall the package from venv
    cython_build.pip_uninstall_package()

    # 2. Remove standard build targets
    targets = [config.BUILD_DIR, "dist", "cython_build"]
    for target in targets:
        if os.path.exists(target):
            shutil.rmtree(target, ignore_errors=True)
            print(f"Removed: {target}")

    # 3. Remove all __pycache__ directories
    for path in glob.glob("**/__pycache__", recursive=True):
        try:
            shutil.rmtree(path)
            print(f"Removed pycache: {path}")
        except Exception as e:
            print(f"Error removing pycache {path}: {e}")

    # 4. Remove all .egg-info directories
    for path in glob.glob("**/*.egg-info", recursive=True):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Removed egg-info: {path}")
            else:
                os.remove(path)
                print(f"Removed egg-info file: {path}")
        except Exception as e:
            print(f"Error removing egg-info {path}: {e}")

    # 5. Clean compiled extensions in src
    clean_src()


def main():
    if "-h" in sys.argv:
        print("-c: clean up old cython build output")
        print("-i: run pyinstaller after cython build")
        print("-w: build wheel and install via pip (default)")
        print("-clean-src: clean compiled extensions")
        print("-clean-exec: clean only build output and dist")
        print("-clean-all: clean all build artifacts")
        sys.exit()

    if "-clean-src" in sys.argv:
        clean_src()
        return

    if "-clean-exec" in sys.argv:
        clean_exec()
        return

    if "-clean-all" in sys.argv:
        clean_all()
        return

    if "-c" in sys.argv:
        # maintain backward compatibility with -c
        clean_all()

    # Build wheel and install via pip (clean installation)
    # We call cython_build() first to get the list of compiled modules for PyInstaller
    my_modules = cython_build.cython_build()
    wheel_path = cython_build.build_wheel()
    cython_build.pip_uninstall_package()
    cython_build.pip_install_wheel(wheel_path)

    print(f"MY_MODULES: {my_modules}")

    if "-i" in sys.argv:
        pyinstaller.build(
            config.PACKAGE_NAME,
            my_modules,
            config.PYINSTALLER_PACKAGES,
            config.PYINSTALLER_HIDDEN_IMPORTS,
            config.PYINSTALLER_METADATA_PACKAGES
        )

if __name__ == "__main__":
    main()
