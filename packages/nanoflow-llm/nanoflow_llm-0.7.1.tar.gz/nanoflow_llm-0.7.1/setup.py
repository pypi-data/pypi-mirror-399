
import os
import platform
from setuptools import setup, Extension
import pybind11

# Read README for PyPI description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# --- OS Detection ---
is_windows = platform.system() == "Windows"

# --- Conditional Flags ---
if is_windows:
    extra_compile_args = ["/O2", "/std:c++14", "/EHsc", "/D_CRT_SECURE_NO_WARNINGS"]
else:
    extra_compile_args = ["-O3", "-std=c++14", "-fPIC", "-pthread"]

# --- Sources ---
sources = [
    os.path.join("src", "nanoflow_core.cpp"),
    os.path.join("src", "bindings.cpp"),
]

# --- Extension Definition ---
ext_modules = [
    Extension(
        "nanoflow_ext",
        sources,
        include_dirs=[
            pybind11.get_include(),
            "src",
        ],
        extra_compile_args=extra_compile_args,
        language="c++",
    ),
]

setup(
    name="nanoflow_llm",
    version="0.7.1", # Patch version for README update
    description="NanoFlow v0.7: The Universal Sparse Streaming Inference Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mardochée Zousko Nicanor",
    url="https://github.com/nanoflow-llm/engine",
    ext_modules=ext_modules,
    setup_requires=["pybind11"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
