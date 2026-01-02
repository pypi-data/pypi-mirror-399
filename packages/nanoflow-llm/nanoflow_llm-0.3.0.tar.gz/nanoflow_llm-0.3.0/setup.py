from setuptools import setup, Extension
import pybind11
import os

# Define the absolute path to the pre-compiled libraries
# This assumes the notebook environment structure
LIB_DIR = "/content/llama.cpp/build/bin"

# Configuration paths
project_dir = os.path.dirname(os.path.abspath(__file__))
include_dirs = [
    pybind11.get_include(),
    os.path.join(project_dir, "extern/include")
]

# Define the Extension
# We link against the shared libraries found in build/bin instead of recompiling objects
ext_modules = [
    Extension(
        "nanoflow", # Extension name determines the import name (import nanoflow)
        ["src/nanoflow_module.cpp"],
        include_dirs=include_dirs,
        library_dirs=[LIB_DIR],
        libraries=["ggml", "ggml-cpu", "ggml-base"],
        runtime_library_dirs=[LIB_DIR],  # RPATH: Bakes the path into the binary
        language="c++",
        extra_compile_args=["-std=c++14", "-O3", "-fPIC"],
    ),
]

setup(
    name="nanoflow-llm", # Changed package name to avoid conflict/meet requirement
    version="0.3.0",
    description="NanoFlow Inference Engine (Linked)",
    ext_modules=ext_modules,
    zip_safe=False,
)
