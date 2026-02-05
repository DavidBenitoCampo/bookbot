#!/usr/bin/env python3
"""
BookBot - Professional Text Analysis Tool

Setup configuration for package installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="bookbot",
    version="1.0.0",
    author="David Benito Campo",
    author_email="",
    description="Professional text analysis tool for books and documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DavidBenitoCampo/bookbot",
    project_urls={
        "Bug Tracker": "https://github.com/DavidBenitoCampo/bookbot/issues",
        "Documentation": "https://github.com/DavidBenitoCampo/bookbot#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Education",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "colorama>=0.4.6",
        "tabulate>=0.9.0",
    ],
    extras_require={
        "visualize": [
            "matplotlib>=3.5.0",
            "wordcloud>=1.8.2",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "mypy>=0.990",
            "flake8>=5.0.0",
        ],
        "all": [
            "matplotlib>=3.5.0",
            "wordcloud>=1.8.2",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bookbot=bookbot.cli:main",
        ],
    },
    include_package_data=True,
    keywords="text analysis, books, nlp, word frequency, reading statistics",
)
