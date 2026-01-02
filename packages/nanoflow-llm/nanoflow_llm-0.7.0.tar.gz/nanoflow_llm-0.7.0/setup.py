
import os
import platform
from setuptools import setup, Extension
import pybind11

# --- OS Detection ---
is_windows = platform.system() == "Windows"

# --- Compiler Flags ---
if is_windows:
    # MSVC Flags
    # /EHsc: Enable standard C++ exception handling
    # /O2: Optimize for speed
    extra_compile_args = ["/O2", "/std:c++14", "/EHsc", "/D_CRT_SECURE_NO_WARNINGS"]
else:
    # GCC/Clang Flags
    # -fPIC: Position Independent Code
    # -pthread: Enable threading support (Crucial for DiskStreamer)
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
            "src",  # Include local headers
        ],
        extra_compile_args=extra_compile_args,
        language="c++",
    ),
]

setup(
    name="nanoflow_llm",
    version="0.7.0",  # Major update for Sparse Streaming
    description="NanoFlow v0.7: Sparse Streaming Inference Engine",
    long_description="An I/O-bound inference engine optimized for running massive models on consumer hardware via sparse tiling.",
    ext_modules=ext_modules,
    setup_requires=["pybind11"],
)
