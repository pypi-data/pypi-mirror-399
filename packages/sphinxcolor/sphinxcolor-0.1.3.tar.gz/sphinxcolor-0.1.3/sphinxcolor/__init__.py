#!/usr/bin/env python3

# File: sphinxcolor/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

"""
sphinxcolor - Colorize Sphinx build output
A package to add beautiful colors to sphinx-build output using regex patterns.

Can be used as:
1. Pipe: sphinx-build ... | sphinxcolor
2. Sphinx extension: Add 'sphinxcolor' to extensions in conf.py
3. Direct execution: python -m sphinxcolor < output.txt
"""

from .__version__ import version  # type: ignore

__version__ = version
__author__ = "Hadi Cahyadi"

from .config import Config
from .colorizer import SphinxColorizer, colorize_line
from .extension import setup

__all__ = ["Config", "SphinxColorizer", "colorize_line", "setup"]