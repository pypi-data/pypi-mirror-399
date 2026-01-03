"""
Setup script for KanervaSDM package.

(c) 2026 Simon Wong.
"""

from setuptools import setup, Extension, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys
import os

__version__ = "1.0.0"

# Get the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

ext_modules = [
    Pybind11Extension(
        "kanerva_sdm._kanerva_sdm",
        [os.path.join("src", "kanerva_sdm", "bindings.cpp")],
        include_dirs=[
            os.path.join(here, "include"),
        ],
        define_macros=[("VERSION_INFO", f'"{__version__}"')],
        cxx_std=11,
    ),
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="KanervaSDM",
    version=__version__,
    author="Simon Wong",
    author_email="smw2@ualberta.ca",  
    description="Sparse Distributed Memory implementation based on Kanerva (1992)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/made-by-simon/KanervaSDM", 
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
    ],
    extras_require={
        "test": ["pytest>=6.0"],
        "dev": ["pytest>=6.0", "black", "flake8"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    keywords="sparse distributed memory, SDM, Kanerva, neural networks, cognitive models",
    project_urls={
        "Bug Reports": "https://github.com/made-by-simon/KanervaSDM/issues",
        "Source": "https://github.com/made-by-simon/KanervaSDM",
        "Documentation": "https://github.com/made-by-simon/KanervaSDM#readme",
    },
)