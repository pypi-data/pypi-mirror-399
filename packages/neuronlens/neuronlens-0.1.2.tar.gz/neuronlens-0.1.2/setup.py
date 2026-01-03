"""
Setup script for neuronlens package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "cloud_api" / "neuronlens" / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text()

# Core requirements for the neuronlens package
# These are the minimum dependencies needed for the package to work
install_requires = [
    "requests>=2.31.0",
    "numpy>=1.24.0",
]

# Optional dependencies for additional functionality
extras_require = {
    # For loading .env files (used in test scripts and examples)
    "env": ["python-dotenv>=1.0.0"],
    # Full installation includes all optional dependencies
    "all": [
        "python-dotenv>=1.0.0",
    ],
}

setup(
    name="neuronlens",
    version="0.1.2",
    description="Python package for NeuronLens interpretability analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NeuronLens Team",
    packages=find_packages(where="cloud_api"),
    package_dir={"": "cloud_api"},
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
