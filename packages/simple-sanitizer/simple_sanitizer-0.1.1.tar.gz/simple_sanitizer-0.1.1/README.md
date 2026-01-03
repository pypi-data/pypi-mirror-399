# simple-sanitizer
![PyPI - Version](https://img.shields.io/pypi/v/simple-sanitizer)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/simple-sanitizer)
![License](https://img.shields.io/badge/license-MIT-green)

a simple python sanitizer kickoff package.  

> **⚠️ Disclaimer:** This project is a **educational exercise** created for learning Python packaging, testing, and distribution workflows. It is **not intended for production use**. For professional sanitization needs, please consider established libraries like `bleach` or `python-magic`.

---

## 🛠 Development Setup

If you want to contribute to this project or run tests locally, follow these steps to set up your professional development environment.

### 1. Prerequisites
- **Python 3.12** or higher.
- `git` installed on your system.

### 2. Installation Steps

Clone the repository and navigate into the project directory:
```bash
git clone https://github.com/luojiakickoff/simple-sanitizer.git
cd simple-sanitizer
```

Create a virtual environment to keep your global Python installation clean:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the package in **editable mode** with all development dependencies:
```bash
pip install -r requirements-dev.txt
```
>> **Note:** The -r command reads our requirement file, which contains the -e .[dev] flag.  
1. -e (Editable): Changes to your source code in src/ are reflected immediately without re-installing.
2. .[dev]: Automatically installs optional tools like pytest and ruff defined in setup.py.

### 3. Quality Control Workflow
Before committing your code, please ensure it passes our quality standards:

#### Running Tests
We use `pytest` for unit testing. All tests must pass:
```bash
pytest
```

#### Linting & Formatting
We use `ruff` to maintain a consistent coding style (Google Style).
```bash
# Check for linting errors
ruff check .

# Format code automatically
ruff format .
```

### 4. Project Structure Reference
- `src/simple_sanitizer/`: Main logic (Production code).
- `tests/`: Test suites for all modules.
- `setup.py`: Project metadata and dependency definitions.
- `pyproject.toml`: Configuration for build systems and tools (Ruff).


---

## 📦 Distribution (Building the Package)

This project follows the **PEP 517** standard, using `build` as the frontend and `setuptools` as the backend.

### 1. Build the Distribution
To generate distribution archives (such as `.whl` and `.tar.gz`) from the source code, run:

```bash
# Install the build tool
pip install build

# Run the build process
python -m build
```
Once the process is complete, you will find the generated files in the dist/ directory:

- `simple_sanitizer-0.1.0-py3-none-any.whl` (Recommended binary distribution)
- `simple_sanitizer-0.1.0.tar.gz` (Source distribution)

### 2. Local Installation & Verification
Before publishing, you can verify the package by installing it locally:
```bash
pip install dist/simple_sanitizer-0.1.0-py3-none-any.whl
```


---

## 🚀 Release Workflow
Maintainers should follow these steps to release a new version:

### 1. Commit and Tag
Ensure all code passes pytest and ruff checks. Then, tag the release in Git:
```bash
# Add and commit the changes
git add .
git commit -m "chore: prepare release v0.1.0"

# Make a tag and push/merge it to main branch and tag it
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin main --tags
```

### 2. GitHub Release
1. Navigate to the **Releases** section on your GitHub repository page.
2. Click ***Draft a new release* and select the `v0.1.0` tag.
3. Drag and drop the files from the `dist/` directory into the ***Assets* area.
4. Click **Publish release**.

### 3. Publish to PyPI
Use **twine** to upload your package to the Python Package Index:
```bash
# Install the upload tool
pip install twine

# Upload to PyPI (API Token required)
python -m twine upload dist/*
```
