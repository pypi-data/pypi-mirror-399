import os
import codecs
import re
from setuptools import find_packages, setup

def read_path(rel_path: str) -> str:
    """Read a file relative to this script's directory."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r", "utf-8") as fp:
        return fp.read()
    
def get_version(rel_path: str) -> str:
    """Get the version from the specified file."""
    version_file = read_path(rel_path)
    version_match = re.search(r'^__version__\s*=\s*["\']([^"\']*)["\']', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="simple-sanitizer",
    version=get_version("src/simple_sanitizer/__init__.py"),
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # Production dependencies (Empty for now)
    install_requires=[],
    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest>=9.0.2",
            "ruff>=0.14.10",
        ],
    },
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
