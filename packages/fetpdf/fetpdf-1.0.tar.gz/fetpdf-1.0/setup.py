# pylint: disable=missing-function-docstring
# pylint: disable=missing-function-docstring

import setuptools
from pathlib import Path

setuptools.setup(
    name="fetpdf",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["test", "data"])
)
