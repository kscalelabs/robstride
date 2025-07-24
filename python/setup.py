from setuptools import setup, find_packages
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
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=["tabulate", "click>=8.0.0"],
    python_requires=">=3.12",
    entry_points={
        'console_scripts': [
            'robstride=robstride_cli.cli:cli',
            'robstride-param-dump=param_dump:main',
            'robstride-scan=scan_actuators:main',
        ],
    },
)