import setuptools
from pathlib import Path

setuptools.setup(
    name="annazpdf",
    version="1.0.0",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests", "data"]),
)
