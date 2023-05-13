from setuptools import setup, Extension
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
    name="nazo_image_utils",
    ext_modules=cythonize(
        Extension(
            "",
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
    author="bymoye",
    author_email="s3moye@gmail.com",
    version="0.0.1",
    description="A tool for generating random images",
    license="MIT",
    package_data={
        "": [
            "nazo_image_utils/rand_image.pyi",
            "nazo_image_utils/rand_image.pyx",
            "nazo_image_utils/process_image.py",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Cython",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    packages=["nazo_image_utils"],
)
