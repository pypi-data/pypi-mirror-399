
import os
import platform
from setuptools import setup, Extension
import pybind11

# --- OS Detection ---
is_windows = platform.system() == "Windows"

# --- Conditional Flags ---
if is_windows:
    extra_compile_args = ["/O2", "/std:c++14", "/MD"]
    obj_ext = ".obj"
else:
    extra_compile_args = ["-O3", "-std=c++14", "-fPIC"]
    obj_ext = ".o"

# --- Paths & Objects ---
lib_dir = os.path.join("extern", "libs")
# Check if sources exist to prevent build crash in incomplete envs
sources = [
    os.path.join("src", "nanoflow_bindings.cpp"),
]

# --- Extension Definition ---
ext_modules = []

# Only attempt to build extension if source exists
if os.path.exists(sources[0]):
    extra_objects = []
    obj_path = os.path.join(lib_dir, f"ggml{obj_ext}")
    
    # Add external object only if it exists
    if os.path.exists(obj_path):
        extra_objects.append(obj_path)

    ext_modules = [
        Extension(
            "nanoflow_ext",
            sources,
            include_dirs=[
                pybind11.get_include(),
                os.path.join("extern", "include"),
            ],
            extra_compile_args=extra_compile_args,
            extra_objects=extra_objects,
            language="c++",
        ),
    ]

setup(
    name="nanoflow_llm",
    version="0.4.1",
    description="NanoFlow LLM Bindings (Cross-Platform)",
    ext_modules=ext_modules,
)
