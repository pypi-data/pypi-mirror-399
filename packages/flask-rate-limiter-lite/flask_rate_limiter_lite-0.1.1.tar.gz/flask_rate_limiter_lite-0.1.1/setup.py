from setuptools import setup, find_packages

setup(
    name="flask-rate-limiter-lite",
    author="Aayushi Singh",
    version="0.1.1",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=["flask", "pydantic"],
)
