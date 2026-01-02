"""
Setup script for ProleTRact with Cython support.
"""
from setuptools import setup, Extension, find_packages
from pathlib import Path

# Try to import Cython - if not available, extensions will be skipped
try:
    from Cython.Build import cythonize
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False
    # Create a dummy cythonize function
    def cythonize(extensions, **kwargs):
        return []

# Try to import numpy - if not available, we'll skip include_dirs
try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Get the project root directory
project_root = Path(__file__).parent
src_path = project_root / "src"

# Define Cython extensions (only if Cython is available)
extensions = []
if HAS_CYTHON:
    include_dirs = []
    if HAS_NUMPY and hasattr(numpy, 'get_include'):
        include_dirs = [numpy.get_include()]
    
    extensions = [
        Extension(
            "proletract.modules.io.fast_parsing",
            [str(src_path / "proletract" / "modules" / "io" / "fast_parsing.pyx")],
            include_dirs=include_dirs,
            extra_compile_args=['-O3'],
            language="c",
        ),
    ]

# Read requirements
requirements = []
requirements_path = project_root / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Add Cython to requirements if not present
if 'cython' not in [r.lower() for r in requirements]:
    requirements.append('cython>=0.29.0')

setup(
    name="proleTRact",
    version="0.2.0",
    description="A user-friendly platform for interactive exploration, visualization, and analysis of tandem repeat findings from TandemTwister outputs",
    license="BSD 3-Clause Non-Commercial License",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        },
        build_dir="build",
    ) if HAS_CYTHON and extensions else [],
    install_requires=requirements,
    python_requires=">=3.9",
    zip_safe=False,
)

