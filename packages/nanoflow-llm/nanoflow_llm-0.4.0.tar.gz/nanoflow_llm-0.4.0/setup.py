
from setuptools import setup, Extension
import pybind11
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
include_dirs = [
    pybind11.get_include(),
    os.path.join(project_dir, "extern/include"),
    os.path.join(project_dir, "extern/src")
]

# Explicitly list the object files we just compiled
extra_objects = ['/content/llama.cpp/NanoFlow/extern/src/ggml.c.o', '/content/llama.cpp/NanoFlow/extern/src/ggml-alloc.c.o', '/content/llama.cpp/NanoFlow/extern/src/ggml-quants.c.o', '/content/llama.cpp/NanoFlow/extern/src/ggml-backend.cpp.o']

ext_modules = [
    Extension(
        "nanoflow",
        ["src/nanoflow_module.cpp"],
        include_dirs=include_dirs,
        extra_objects=extra_objects,
        language="c++",
        extra_compile_args=['-std=c++14', '-O3', '-fPIC', '-D_GNU_SOURCE'],
    ),
]

setup(
    name="nanoflow-llm",
    version="0.4.0",
    description="NanoFlow Inference Engine (Standalone Build)",
    ext_modules=ext_modules,
    zip_safe=False,
)
