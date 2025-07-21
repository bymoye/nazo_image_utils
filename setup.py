from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
from Cython.Compiler import Options
from sys import platform


extra_compile_args = []
extra_link_args = []

if platform == "win32":
    extra_compile_args = ["/std:c++17", "/O2"]
elif platform == "linux":
    extra_compile_args = ["-std=c++17", "-O3"]
    extra_link_args = ["-Wl,-O3"]
elif platform == "darwin":  # macOS
    extra_compile_args = ["-std=c++17", "-O3"]
    extra_link_args = ["-Wl,-dead_strip"]

Options.cimport_from_pyx = False

setup(
    packages=find_packages(exclude=["wheelhouse", "venv", "build", "dist"]),
    ext_modules=cythonize(
        Extension(
            "nazo_image_utils.rand_image",
            sources=["./nazo_image_utils/rand_image.pyx"],
            language="c++",
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
        ),
        compiler_directives={
            "language_level": 3,
            "boundscheck": False,
            "wraparound": False,
            "binding": True,
        },
    ),
    package_data={
        "nazo_image_utils": [
            "rand_image.pyi",
            "rand_image.pyx",
            "process_image.py",
            "__init__.py",
        ]
    },
    include_package_data=True,
)
