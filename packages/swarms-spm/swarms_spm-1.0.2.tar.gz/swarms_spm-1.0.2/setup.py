"""
Setup script for spm package.

This file is kept for backward compatibility. The package is configured
via pyproject.toml using setuptools as the build backend.
"""

from setuptools import setup

# Read the README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="spm",
    version="1.0.0",
    author="Swarms Team",
    description="A lightweight, standalone library for managing hierarchical system prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/spm",
    packages=["spm"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],  # No dependencies
)

