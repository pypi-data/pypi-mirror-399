
import os
import platform
from setuptools import setup, Extension
import pybind11

is_windows = platform.system() == "Windows"

if is_windows:
    extra_compile_args = ["/O2", "/std:c++14", "/EHsc", "/D_CRT_SECURE_NO_WARNINGS"]
else:
    extra_compile_args = ["-O3", "-std=c++14", "-fPIC", "-pthread"]

sources = [
    os.path.join("src", "nanoflow_core.cpp"),
    os.path.join("src", "bindings.cpp"),
]

ext_modules = [
    Extension(
        "nanoflow_ext_v7", # <--- RENAMED HERE
        sources,
        include_dirs=[pybind11.get_include(), "src"],
        extra_compile_args=extra_compile_args,
        language="c++",
    ),
]

setup(
    name="nanoflow_llm_v7",
    version="0.7.1",
    description="NanoFlow v0.7 Sparse Engine",
    ext_modules=ext_modules,
    setup_requires=["pybind11"],
)
