from setuptools import setup

setup(
    name="fdir-cli",
    version="2.0.0",
    py_modules=["fdir"],
    entry_points={
        "console_scripts": [
            "fdir = fdir:main",
        ],
    },
    python_requires=">=3.8",
    description="Command-line utility to list, filter, and sort files in a directory",
)