from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import re
import sys
import glob
import subprocess
import shutil

import config


def get_export_name(file_path):
    relative_path = os.path.relpath(file_path, config.SRC_DIR)
    module_name = os.path.splitext(relative_path)[0].replace(os.path.sep, ".")
    print(f"Module: {module_name}")
    return module_name


def cython_build():
    """
    Compile Cython extensions in-place (for development).
    Output: .pyd/.so files in src/ directory.
    """
    src_pattern = os.path.join(config.SRC_DIR, "**", "*.py")
    all_py_files = glob.glob(src_pattern, recursive=True)

    extensions = []
    my_modules = []
    for file in all_py_files:
        module_name = get_export_name(file)
        # Skip __init__ and __main__ modules to avoid package execution issues
        if not module_name.endswith(".__main__"):
            my_modules.append(module_name)
            extensions.append(Extension(module_name, [file]))

    # Correctly trigger build_ext --inplace by modifying sys.argv
    old_argv = sys.argv[:]
    sys.argv = [sys.argv[0], "build_ext", "--inplace"]
    try:
        setup(
            name=config.PACKAGE_NAME,
            version=config.VERSION,
            package_dir={"": "src"},
            packages=find_packages(where="src"),
            ext_modules=cythonize(
                extensions,
                compiler_directives=config.CYTHON_DIRECTIVES,
                build_dir=config.CYTHON_DIR,
            ),
        )
    finally:
        sys.argv = old_argv

    return my_modules


def build_wheel():
    """
    Build wheel distribution from a temporary directory containing only binary extensions.
    Output: dist/rag-0.1-*.whl
    """
    print("Building secure wheel...")

    # 1. Ensure Cython extensions are compiled in-place first
    cython_build()

    # 2. Prepare temporary directory for distribution
    dist_prep_dir = os.path.join(config.BUILD_DIR, "wheel_prep")
    if os.path.exists(dist_prep_dir):
        shutil.rmtree(dist_prep_dir)
    os.makedirs(dist_prep_dir)

    # 3. Copy package from src to prep dir
    pkg_src = os.path.join(config.SRC_DIR, config.PACKAGE_NAME)
    pkg_dest = os.path.join(dist_prep_dir, config.PACKAGE_NAME)
    shutil.copytree(pkg_src, pkg_dest)

    # 4. Remove .py files except __init__.py to secure code
    for root, dirs, files in os.walk(pkg_dest):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removing source file for security: {file_path}")

    # 5. Create a minimal setup.py for packaging
    setup_content = f"""
from setuptools import setup, find_packages
setup(
    name="{config.PACKAGE_NAME}",
    version="{config.VERSION}",
    packages=find_packages(),
    package_dir={{"": "."}},
    package_data={{"{config.PACKAGE_NAME}": ["*.so", "utils/*.so"]}},
)
"""
    with open(os.path.join(dist_prep_dir, "setup.py"), "w") as f:
        f.write(setup_content)

    # 6. Build the wheel from the prep directory
    print("Executing bdist_wheel from prep directory...")
    result = subprocess.run(
        [sys.executable, "setup.py", "bdist_wheel"],
        cwd=dist_prep_dir
    )

    if result.returncode != 0:
        raise RuntimeError("Failed to build wheel")

    # 7. Move the wheel to the final dist directory
    dist_dir = os.path.join(config.BASE_DIR, "dist")
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)

    wheel_pattern = os.path.join(dist_prep_dir, "dist", "*.whl")
    wheels = glob.glob(wheel_pattern)
    if not wheels:
        raise RuntimeError("No wheel file found in prep/dist/")

    final_wheel_path = os.path.join(dist_dir, os.path.basename(wheels[0]))
    shutil.move(wheels[0], final_wheel_path)

    print(f"Built secure wheel: {final_wheel_path}")
    return final_wheel_path



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
    
    result = subprocess.run(cmd, cwd=config.BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to install wheel: {wheel_path}")
    
    print(f"Installed: {wheel_path}")


def pip_uninstall_package():
    """
    Uninstall the package (for clean reinstall).
    """
    print(f"Uninstalling {config.PACKAGE_NAME}...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", config.PACKAGE_NAME],
        cwd=config.BASE_DIR
    )
    # Ignore error if package not installed
    if result.returncode == 0:
        print(f"Uninstalled: {config.PACKAGE_NAME}")
    else:
        print(f"{config.PACKAGE_NAME} was not installed")
