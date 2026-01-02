
from setuptools import setup, Extension
import pybind11
import os
import platform

# Base Configuration
project_dir = os.path.dirname(os.path.abspath(__file__))
include_dirs = [
    pybind11.get_include(),
    os.path.join(project_dir, "extern/include")
]

# Platform-specific Configuration
system = platform.system()
extra_compile_args = []
extra_objects = []
library_dirs = []
libraries = []
runtime_library_dirs = []

if system == "Windows":
    print("Configuring for Windows...")
    extra_compile_args = ['/std:c++14', '/O2']
    
    # Look for static object files for Windows linking
    libs_path = os.path.join(project_dir, "extern", "libs")
    if os.path.exists(libs_path):
        extra_objects = [
            os.path.join(libs_path, f) 
            for f in os.listdir(libs_path) 
            if f.endswith(".obj")
        ]
else:
    print("Configuring for Linux/Unix...")
    # Linux Build Flags
    extra_compile_args = ['-std=c++14', '-O3', '-fPIC']
    
    # Link against shared libraries built in the Colab environment
    LIB_DIR = "/content/llama.cpp/build/bin"
    library_dirs = [LIB_DIR]
    libraries = ["ggml", "ggml-cpu", "ggml-base"]
    runtime_library_dirs = [LIB_DIR]

# Define Extension
ext_modules = [
    Extension(
        "nanoflow",
        ["src/nanoflow_module.cpp"],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        runtime_library_dirs=runtime_library_dirs,
        extra_objects=extra_objects,
        language="c++",
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name="nanoflow-llm",
    version="0.3.2",
    description="NanoFlow Inference Engine (Cross-Platform)",
    ext_modules=ext_modules,
    zip_safe=False,
)
