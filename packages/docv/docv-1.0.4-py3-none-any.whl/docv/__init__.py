#!/usr/bin/env python3

# File: docv/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT

from .docs import API, find_html_file, load_shortcuts, get_vim_js, print_shortcuts

from .__version__ import version

__all__ = [
	"API",
	"find_html_file",
	"load_shortcuts",
	"get_vim_js",
]
__version__ = version