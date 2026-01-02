#!/usr/bin/env python3

# File: setup.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-29
# Description: 
# License: MIT
# -*- coding: utf-8 -*-

import os.path
from setuptools import setup
import shutil
from pathlib import Path
import traceback

NAME = "docv"

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

    return "1.0.0"

def get_requirements():
    """
    Get the requirements from requirements.txt file.
    """
    requirements = []
    try:
        req_file = Path(__file__).parent / "requirements.txt"
        if req_file.is_file():
            with open(req_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        requirements.append(line)
    except Exception as e:
        if os.getenv('TRACEBACK') and os.getenv('TRACEBACK') in ['1', 'true', 'True']:
            print(traceback.format_exc())
        else:
            print(f"ERROR: {e}")

    return requirements


try:
    shutil.copy2("__version__.py", f"{NAME}/__version__.py")
except IOError:
    pass
except Exception as e:
    print("Unexpected error:", e)

here = os.path.dirname(os.path.abspath(__file__))


setup(name='docv',
    version=get_version(),
    description=('A powerful documentation viewer with Vimium-C style keyboard navigation and fully customizable shortcuts.'),
    long_description=open(os.path.join(here, 'README.md')).read(),
    long_description_content_type="text/markdown",
    author='Hadi Cahyadi',
    author_email='cumulus13@gmail.com',
    maintainer='cumulus13',
    maintainer_email='cumulus13@gmail.com',
    url='http://github.com/cumulus13/docs',
    packages=['docv'],
    install_requires=get_requirements(),
    extras_require={'all': ['webview', 'envdot']},
    keywords='documentation viewer vimium-c shortcuts custom',
    entry_points={
        'console_scripts': [
            'docs=docv.docs:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Documentation',
        ],
    platforms='any',
    license='MIT',
    license_files=['LICENSE']
)
