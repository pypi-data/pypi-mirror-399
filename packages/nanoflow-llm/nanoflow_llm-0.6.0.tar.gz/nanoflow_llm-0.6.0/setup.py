
import os
import platform
from setuptools import setup, Extension
import pybind11

# --- OS Detection ---
is_windows = platform.system() == "Windows"

# --- Conditional Flags ---
if is_windows:
    # MSVC Flags
    extra_compile_args = ["/O2", "/std:c++14", "/MD", "/D_CRT_SECURE_NO_WARNINGS"]
    obj_ext = ".obj"
else:
    # GCC/Clang Flags
    extra_compile_args = ["-O3", "-std=c++14", "-fPIC", "-w"] # -w to suppress ggml warnings
    obj_ext = ".o"

# --- Paths ---
ggml_root = os.path.join("extern", "ggml")
ggml_include = os.path.join(ggml_root, "include")
ggml_src = os.path.join(ggml_root, "src")

# --- Sources ---
# We compile GGML from source to ensure simple linking in this environment
sources = [
    os.path.join("src", "engine.cpp"),
    os.path.join("src", "bindings.cpp"),
    # Core GGML files
    os.path.join(ggml_src, "ggml.c"),
    os.path.join(ggml_src, "ggml-alloc.c"),
    os.path.join(ggml_src, "ggml-backend.cpp"),
    os.path.join(ggml_src, "ggml-quants.c"),
    os.path.join(ggml_src, "ggml-threading.cpp"), # Required for critical sections
]

# --- Extension Definition ---
ext_modules = [
    Extension(
        "nanoflow_ext",
        sources,
        include_dirs=[
            pybind11.get_include(),
            "src",         # For engine.h
            ggml_include,  # For ggml.h
            ggml_src,      # For internal headers like ggml-impl.h
        ],
        extra_compile_args=extra_compile_args,
        define_macros=[
            ("GGML_VERSION", '\"0.6.0\"'), 
            ("GGML_COMMIT", '\"unknown\"')
        ],
        language="c++",
    ),
]

setup(
    name="nanoflow_llm",
    version="0.6.0",
    description="NanoFlow LLM Universal Bindings (Self-Contained)",
    ext_modules=ext_modules,
)
