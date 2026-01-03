from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

setup(
    name="logicalbin",
    version="1.0",
    author="BlueJFlamesLab",
    long_description=(this_directory / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.0",
    license="MIT",
)
