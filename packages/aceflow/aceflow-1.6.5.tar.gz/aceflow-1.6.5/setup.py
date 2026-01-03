import sys
import os
from setuptools import setup, Extension
import numpy as np

# --- 1. Rust Handling ---
try:
    from setuptools_rust import RustExtension, Binding
except ImportError:
    import warnings
    warnings.warn("setuptools-rust not found. Rust extensions will not be built.")
    RustExtension = None
    Binding = None

# --- 2. C Extension Configuration ---
include_dirs = [np.get_include(), 'aceflow/core/c_core']

is_windows = sys.platform.startswith('win')
is_mac = sys.platform == 'darwin'

# Default flags
compile_args = []
link_args = []
macros = []

if is_windows:
    compile_args = ['/O2', '/GL']
elif is_mac:
    # Mac usually uses Clang, OpenMP is often tricky on Mac, disabling for safety
    # or use specific paths if you have libomp installed via brew
    compile_args = ['-O3', '-march=native']
else:
    # Linux
    compile_args = ['-O3', '-march=native', '-fopenmp']
    link_args = ['-fopenmp']
    macros = [('_OPENMP', None)]

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

# --- 3. Rust Extension Configuration ---
rust_extensions = []
if RustExtension:
    # We look for the cargo file relative to this setup.py
    cargo_path = os.path.join("aceflowcore", "Cargo.toml")
    
    if os.path.exists(cargo_path):
        rust_extensions.append(
            RustExtension(
                "aceflowcore",
                path=cargo_path,
                binding=Binding.PyO3,
                native=False,
                py_limited_api=False,
                features=[],
            )
        )
    else:
        # If packaging properly via MANIFEST.in, this should exist. 
        # If it doesn't, we warn the user.
        print(f"WARNING: Rust source not found at {cargo_path}. Rust extension will be skipped.")

setup(
    ext_modules=extensions,
    rust_extensions=rust_extensions,
)