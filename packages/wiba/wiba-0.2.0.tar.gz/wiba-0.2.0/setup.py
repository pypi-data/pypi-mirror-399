from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wiba",
    version="0.2.0",
    author="Arman Irani",
    author_email="airan002@ucr.edu",
    description="WIBA: What Is Being Argued? A Comprehensive Approach to Argument Mining",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Armaniii/WIBA",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pandas>=1.2.0",
        "numpy>=1.19.0",
        "tqdm>=4.50.0",
        "structlog>=21.1.0",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/Armaniii/WIBA/issues",
        "Documentation": "https://wiba.dev",
        "Source Code": "https://github.com/Armaniii/WIBA",
    },
) 