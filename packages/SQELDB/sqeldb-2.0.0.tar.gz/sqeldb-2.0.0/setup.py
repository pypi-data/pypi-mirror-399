from setuptools import setup
from pathlib import Path

# Paths
this_directory = Path(__file__).parent

# Read README and CHANGELOG
readme = (this_directory / "README.md").read_text(encoding="utf-8")
changelog = (this_directory / "CHANGELOG.md").read_text(encoding="utf-8")
long_description = readme + "\n\n" + changelog  # Combine them

setup(
    name="SQELDB",          # Your package name (must be unique on PyPI)
    version="2.0.0",        # Current version
    py_modules=["ELDB_engine"],  # Your module
    install_requires=[],    # Add dependencies if any
    author="Baraa",
    author_email="cenomi3041@gavrom.com",
    description="A simple ELDB engine for Python",
    long_description=long_description,                 # Combined README + CHANGELOG
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
