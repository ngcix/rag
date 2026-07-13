from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import re
import sys
import glob
import subprocess

from config import *


def get_export_name(file_path):
    relative_path = os.path.relpath(file_path, SRC_DIR)
    module_name = os.path.splitext(relative_path)[0].replace(os.path.sep, ".")
    print(f"Module: {module_name}")
    return module_name


def cython_build():
    """
    Compile Cython extensions in-place (for development).
    Output: .pyd/.so files in src/ directory.
    """
    src_pattern = os.path.join(SRC_DIR, "**", "*.py")
    all_py_files = glob.glob(src_pattern, recursive=True)

    extensions = []
    for file in all_py_files:
        module_name = get_export_name(file)
        if not module_name.endswith(".__init__"):
            MY_MODULES.append(module_name)
        extensions.append(Extension(module_name, [file]))

    setup(
        name=PACKAGE_NAME,
        version="0.1",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        ext_modules=cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "embedsignature": True,
            },
            build_dir=CYTHON_DIR,
        ),
        script_args=["build_ext", "--inplace"],
    )


def build_wheel():
    """
    Build wheel distribution from setup.py.
    Output: dist/rag-0.1-*.whl
    """
    print("Building wheel...")
    result = subprocess.run(
        [sys.executable, "setup.py", "bdist_wheel"],
        cwd=BASE_DIR
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to build wheel")
    
    # Find the built wheel
    wheel_pattern = os.path.join(BASE_DIR, "dist", "*.whl")
    wheels = glob.glob(wheel_pattern)
    if not wheels:
        raise RuntimeError("No wheel file found in dist/")
    
    wheel_path = wheels[0]
    print(f"Built wheel: {wheel_path}")
    return wheel_path


def pip_install_wheel(wheel_path, upgrade=True):
    """
    Install wheel using pip (clean, tracked installation).
    
    Args:
        wheel_path: Path to the .whl file
        upgrade: If True, use --upgrade flag
    """
    print(f"Installing wheel: {wheel_path}")
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.append(wheel_path)
    
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to install wheel: {wheel_path}")
    
    print(f"Installed: {wheel_path}")


def pip_uninstall_package():
    """
    Uninstall the package (for clean reinstall).
    """
    print(f"Uninstalling {PACKAGE_NAME}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", PACKAGE_NAME],
        cwd=BASE_DIR
    )
    # Ignore error if package not installed
    if result.returncode == 0:
        print(f"Uninstalled: {PACKAGE_NAME}")
    else:
        print(f"{PACKAGE_NAME} was not installed")
