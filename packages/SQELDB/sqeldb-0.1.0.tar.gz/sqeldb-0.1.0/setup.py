from setuptools import setup

setup(
    name="SQELDB",          # Your package name (must be unique on PyPI)
    version="0.1.0",              # Start with 0.1.0
    py_modules=["ELDB_engine"],  # Your single file module
    install_requires=[],          # Add dependencies if you have any
    author="Baraa",
    author_email="cenomi3041@gavrom.com",
    description="A simple ELDB engine for Python",
    long_description=open("README.md").read() if True else "",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)