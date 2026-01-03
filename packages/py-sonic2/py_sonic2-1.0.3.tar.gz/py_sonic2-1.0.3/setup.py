#!/usr/bin/env python3

"""
This file is part of py-sonic.

py-sonic is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

py-sonic is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with py-sonic.  If not, see <http://www.gnu.org/licenses/>
"""

from setuptools import setup
import os
import re

# Read version from libsonic/__init__.py without importing it
version_file = os.path.join(os.path.dirname(__file__), "libsonic", "__init__.py")
with open(version_file) as f:
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string.")

req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
requirements = [line.strip() for line in open(req_file) if line.strip() and not line.startswith("#")]

# Read the long description from README
with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="py-sonic2",
    version=version,
    author="Yannick Schäfer",
    author_email="mail@m00n.dev",
    url="https://github.com/m00n/py-sonic",
    project_urls={
        "Bug Tracker": "https://github.com/m00n/py-sonic/issues",
        "Source Code": "https://github.com/m00n/py-sonic",
    },
    description="A Python wrapper library for the Subsonic REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["libsonic"],
    package_dir={"libsonic": "libsonic"},
    install_requires=requirements,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords="subsonic api music streaming",
)
