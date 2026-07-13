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


def main():

    if "-h" in sys.argv:
        print("-c: clean up old cython build output")
        print("-i: run pyinstaller after cython build")
        print("-w: build wheel and install via pip (default)")
        sys.exit()

    if "-c" in sys.argv:
        build_output = glob.glob(f"{BUILD_DIR}/*")
        for dir in build_output:
            if LIB_DIR_RE.match(dir):
                shutil.rmtree(dir)
        # Also clean dist/
        dist_dir = os.path.join(BASE_DIR, "dist")
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)

    # Build wheel and install via pip (clean installation)
    wheel_path = cython_build.build_wheel()
    cython_build.pip_uninstall_package()
    cython_build.pip_install_wheel(wheel_path)

    print(f"MY_MODULES: {MY_MODULES}")

    if "-i" in sys.argv:
        pyinstaller.build(PACKAGE_NAME, MY_MODULES, PYINSTALLER_PACKAGES, PYINSTALLER_HIDDEN_IMPORTS, PYINSTALLER_METADATA_PACKAGES)


if __name__ == "__main__":
    main()
