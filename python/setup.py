from setuptools import setup
from pyo3_setuptools import Pyo3Extension, build_ext

ext_modules = [
    Pyo3Extension(
        "robstride_driver",
        ["../src/lib.rs"],
        rust_crate_dir="../",
        features=["python"],
    ),
]

setup(
    name="robstride-driver",
    version="0.1.0",
    author="K-Scale Labs",
    description="Python bindings for Robstride servo driver",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=["tabulate"],
    python_requires=">=3.7",
    scripts=["robstride_param_dump.py"],
)