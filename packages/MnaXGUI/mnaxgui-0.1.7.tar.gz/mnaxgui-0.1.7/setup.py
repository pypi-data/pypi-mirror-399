from setuptools import setup, find_packages

setup(
    name="MnaXGUI",
    version="0.1.7",  # incremented from 0.1.5
    packages=find_packages(),
    description="GUI package to make it easy",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="MnaX",
    python_requires='>=3.10',
)

