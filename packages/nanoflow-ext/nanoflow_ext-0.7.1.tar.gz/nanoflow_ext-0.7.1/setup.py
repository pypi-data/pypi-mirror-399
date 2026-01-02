
from setuptools import setup, Extension
import pybind11

cpp_args = ['-std=c++14', '-O3']

ext_modules = [
    Extension(
        'nanoflow_ext',
        ['src/bindings.cpp'],
        include_dirs=[pybind11.get_include()],
        language='c++',
        extra_compile_args=cpp_args,
    ),
]

setup(
    name='nanoflow_ext',
    version='0.7.1',
    author='User',
    description='NanoFlow Low-Level Binding',
    ext_modules=ext_modules,
)
