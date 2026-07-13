from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(
    name="rag",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize("src/rag/**/*.py", language_level="3"),
)
