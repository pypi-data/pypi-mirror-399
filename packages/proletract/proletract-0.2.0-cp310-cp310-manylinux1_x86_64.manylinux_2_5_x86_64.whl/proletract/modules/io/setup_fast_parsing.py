"""
Setup script for compiling Cython extensions.
"""
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "proletract.modules.io.fast_parsing",
        ["src/proletract/modules/io/fast_parsing.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=['-O3', '-march=native'] if hasattr(__builtins__, '__NUMPY_SETUP__') else ['-O3'],
    ),
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
    }),
)

