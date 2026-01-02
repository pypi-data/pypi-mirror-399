
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
# On vérifie si les sources existent pour éviter un crash lors du build sans fichiers
sources = [
    os.path.join("src", "nanoflow_bindings.cpp"),
]

# --- Extension Definition ---
ext_modules = []

# On ne tente de compiler l'extension que si le fichier source est présent
if os.path.exists(sources[0]):
    extra_objects = []
    obj_path = os.path.join(lib_dir, f"ggml{obj_ext}")
    
    # Ajout de l'objet externe s'il existe
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
    version="0.3.4",
    description="NanoFlow LLM Bindings (Cross-Platform)",
    ext_modules=ext_modules,
)
