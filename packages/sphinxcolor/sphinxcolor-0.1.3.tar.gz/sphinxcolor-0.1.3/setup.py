#!/usr/bin/env python3
# File: setup.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-27
# Description: Setup configuration for sphinxcolor
# License: MIT

"""Setup configuration for sphinxcolor"""
from setuptools import setup, find_packages
from pathlib import Path
import os
import traceback
import shutil

NAME = "sphinxcolor"

try:
    shutil.copy2("__version__.py", f"{NAME}/__version__.py")
except Exception:
    print("Could not copy __version__.py file.")


def get_version():
    """
    Get the version of the ddf module.
    Version is taken from the __version__.py file if it exists.
    The content of __version__.py should be:
    version = "0.33"
    """
    try:
        version_file = Path(__file__).parent / "__version__.py"
        if not version_file.is_file():
            version_file = Path(__file__).parent / NAME / "__version__.py"
        if version_file.is_file():
            with open(version_file, "r") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        parts = line.split("=")
                        if len(parts) == 2:
                            return parts[1].strip().strip('"').strip("'")
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return "0.1.0"

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name=NAME,
    version=get_version(),
    author="Hadi Cahyadi",
    author_email="cumulus13@gmail.com",
    description="Colorize Sphinx build output with customizable colors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cumulus13/sphinxcolor",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Sphinx :: Extension",
    ],
    keywords="sphinx documentation color colorize build output terminal",
    python_requires=">=3.7",
    install_requires=[
        "rich>=13.0.0",
        # "tomli>=2.0.0;python_version<'3.11'",
        "tomli>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "sphinx": [
            "sphinx>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sphinxcolor=sphinxcolor.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sphinxcolor": ["*.toml"],
    },
    project_urls={
        "Homepage": "https://github.com/cumulus13/sphinxcolor",
        "Bug Reports": "https://github.com/cumulus13/sphinxcolor/issues",
        "Source": "https://github.com/cumulus13/sphinxcolor",
        "Documentation": "https://github.com/cumulus13/sphinxcolor/blob/main/README.md",
    },
    license="MIT",
    license_files=["LICENSE"]
)

# End of setup.py
