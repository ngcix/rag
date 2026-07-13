from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import glob
import os

# Filter out __init__.py and __main__.py to avoid package execution issues
# These files should remain as plain .py files in the distribution
all_py_files = glob.glob("src/rag/**/*.py", recursive=True)
extensions = []
for file in all_py_files:
    # Get module name relative to the 'src' directory
    rel_path = os.path.relpath(file, "src")
    module_name = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")

    if not module_name.endswith(".__init__") and not module_name.endswith(".__main__"):
        extensions.append(Extension(module_name, [file]))

setup(
    name="rag",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize(extensions, language_level="3"),
)
