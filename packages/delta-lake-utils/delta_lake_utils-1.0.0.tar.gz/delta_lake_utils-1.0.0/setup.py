from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="delta-lake-utils",
    version="1.0.0",
    author="Nalini Panwar",
    author_email="panwarnalini@gmail.com",
    description="Production-grade utilities for Delta Lake management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/panwarnalini-hub/delta-lake-utils",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyspark>=3.2.0",
        "delta-spark>=2.0.0",
        "click>=8.0.0",
        "pandas>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "delta-utils=delta_utils.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
