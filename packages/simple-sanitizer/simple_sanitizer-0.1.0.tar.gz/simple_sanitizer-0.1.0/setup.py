from setuptools import find_packages, setup

setup(
    name="simple-sanitizer",
    version="0.1.0",
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
)