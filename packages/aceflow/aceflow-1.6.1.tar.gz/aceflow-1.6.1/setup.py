import sys
import os
from setuptools import setup, find_packages, Extension

# 1. Handle Numpy Import Safely
# We delay the import of numpy until the build actually starts
# to prevent errors if setup.py is just being queried for info.
class BuildExt(object):
    def __init__(self, *args, **kwargs):
        pass

try:
    import numpy as np
    # If numpy is available, we can configure the C extensions immediately
    include_dirs = [np.get_include(), 'aceflow/core/c_core']
except ImportError:
    # If numpy is missing (shouldn't happen with pyproject.toml, but good for safety)
    np = None
    include_dirs = ['aceflow/core/c_core']
    print("WARNING: Numpy not found. C Extensions might fail to build if not handled by pyproject.toml")

# 2. Handle Rust Import Safely
try:
    from setuptools_rust import RustExtension, Binding
except ImportError:
    import warnings
    warnings.warn("setuptools-rust not found. Rust extensions will not be built.")
    RustExtension = None
    Binding = None

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()]

# Check if we're on Windows and adjust compilation flags
is_windows = sys.platform.startswith('win')

if is_windows:
    # Windows compilation flags (no OpenMP for simplicity)
    compile_args = ['/O2', '/GL']
    link_args = []
    macros = []
else:
    # Linux/Mac compilation flags
    compile_args = ['-O3', '-march=native', '-fopenmp']
    link_args = ['-fopenmp']
    macros = [('_OPENMP', None)]

# Define C Extensions
extensions = [
    Extension(
        'aceflow._rnn_ops',
        sources=[
            'aceflow/core/c_core/_rnn_ops.c',
            'aceflow/core/c_core/_rnn_extension.c'
        ],
        include_dirs=include_dirs,
        libraries=['m'] if not is_windows else [],
        extra_compile_args=compile_args,
        extra_link_args=link_args,
        define_macros=macros
    ),
    Extension(
        'aceflow._attention_ops',
        sources=[
            'aceflow/core/c_core/_attention_ops.c',
            'aceflow/core/c_core/_attention_extension.c'
        ],
        include_dirs=include_dirs,
        libraries=['m'] if not is_windows else [],
        extra_compile_args=compile_args,
        extra_link_args=link_args,
        define_macros=macros
    )
]

# Define Rust extensions
rust_extensions = []
if RustExtension: 
    try:
        if os.path.exists("aceflow-core/Cargo.toml"):
            rust_extensions.append(
                RustExtension(
                    "aceflow_core",
                    path="aceflow-core/Cargo.toml",
                    binding=Binding.PyO3,  # <--- Fixed: Correct Binding usage
                    native=False,
                    py_limited_api=False,
                    features=[],
                )
            )
        else:
            print("Warning: aceflow-core/Cargo.toml not found. Skipping Rust extension build.")
    except Exception as e:
        print(f"Warning: Could not configure Rust extensions: {e}")

setup(
    name="aceflow",
    version="1.6.1",
    author="Maaz waheed",
    author_email="wwork4287@gmail.com",
    ext_modules=extensions,
    rust_extensions=rust_extensions,
    description="A Python library for building and training Seq2Seq models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/42Wor/aceflow",
    project_urls={
        "Bug Tracker": "https://github.com/42Wor/aceflow/issues",
        "Source Code": "https://github.com/42Wor/aceflow",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)