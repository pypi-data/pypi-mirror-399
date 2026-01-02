from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md file for PyPI description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="flask-rate-limiter-lite",
    author="Aayushi Singh",
    version="0.1.3",  
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "flask",
        "pydantic",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
