# 🚀 Building and Publishing DAG Optimizer to PyPI

Complete guide to building and publishing the DAG Optimizer package to PyPI.

---

## Prerequisites

1. **PyPI Account**
   - Create account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
   - Create account at [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/) (for testing)

2. **API Tokens**
   - Generate API token at [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
   - Generate test token at [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)

3. **Tools**
   ```bash
   pip install build twine
   ```

---

## Step 1: Prepare the Package

### 1.1 Update Version

Update version in three places:

1. **`setup.py`**:
   ```python
   setup(
       name="dagoptimizer",
       version="1.0.0",  # <-- UPDATE THIS
       # ...
   )
   ```

2. **`pyproject.toml`**:
   ```toml
   [project]
   version = "1.0.0"  # <-- UPDATE THIS
   ```

3. **`src/dagoptimizer/__init__.py`**:
   ```python
   __version__ = "1.0.0"  # <-- UPDATE THIS
   ```

### 1.2 Update CHANGELOG

Add release notes to `CHANGELOG.md`:

```markdown
## [1.0.0] - 2025-12-29

### Added
- Initial release
- Adaptive transitive reduction
- PERT/CPM analysis
- 25+ metrics
...
```

### 1.3 Verify Package Structure

Ensure all files are in place:

```
Optimisation_of_DAGs/
├── src/
│   └── dagoptimizer/
│       ├── __init__.py        # Exports and version
│       └── dag_class.py       # Main DAGOptimizer class
├── setup.py                   # Package configuration
├── pyproject.toml             # Modern Python packaging
├── MANIFEST.in                # What files to include
├── README.md                  # PyPI landing page
├── LICENSE                    # MIT License
├── CHANGELOG.md               # Version history
└── requirements.txt           # Dependencies
```

---

## Step 2: Clean Previous Builds

```bash
# Remove old builds
rm -rf build dist *.egg-info
# On Windows:
# rmdir /s /q build dist
# del /s /q *.egg-info
```

---

## Step 3: Build the Package

```bash
# Build source and wheel distributions
python -m build
```

This creates:
- `dist/dagoptimizer-1.0.0.tar.gz` (source distribution)
- `dist/dagoptimizer-1.0.0-py3-none-any.whl` (wheel distribution)

### Verify Build

```bash
# Check package metadata
twine check dist/*

# Should output:
# Checking dist/dagoptimizer-1.0.0.tar.gz: PASSED
# Checking dist/dagoptimizer-1.0.0-py3-none-any.whl: PASSED
```

---

## Step 4: Test Locally

### 4.1 Install Locally

```bash
# Install from local wheel
pip install dist/dagoptimizer-1.0.0-py3-none-any.whl

# Or install in editable mode for development
pip install -e .
```

### 4.2 Test Installation

```bash
# Test import
python -c "from dagoptimizer import DAGOptimizer; print('Success!')"

# Test version
python -c "import dagoptimizer; print(dagoptimizer.__version__)"

# Test basic functionality
python -c "from dagoptimizer import DAGOptimizer; opt = DAGOptimizer([('A', 'B'), ('B', 'C'), ('A', 'C')]); opt.transitive_reduction(); print(f'Works! {opt.graph.number_of_edges()} edges')"
```

---

## Step 5: Publish to TestPyPI (Optional but Recommended)

### 5.1 Configure TestPyPI Credentials

Create `~/.pypirc`:

```ini
[testpypi]
  username = __token__
  password = pypi-YOUR_TEST_PYPI_TOKEN_HERE
```

### 5.2 Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

### 5.3 Test Installation from TestPyPI

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dagoptimizer

# Test
python -c "from dagoptimizer import DAGOptimizer; print('TestPyPI works!')"

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

**Note**: `--extra-index-url https://pypi.org/simple/` is needed to install dependencies from regular PyPI.

---

## Step 6: Publish to PyPI (Production)

### 6.1 Configure PyPI Credentials

Update `~/.pypirc`:

```ini
[pypi]
  username = __token__
  password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
  username = __token__
  password = pypi-YOUR_TEST_PYPI_TOKEN_HERE
```

### 6.2 Upload to PyPI

```bash
twine upload dist/*
```

You'll see:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading dagoptimizer-1.0.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
Uploading dagoptimizer-1.0.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 

View at:
https://pypi.org/project/dagoptimizer/1.0.0/
```

### 6.3 Verify Publication

Visit: [https://pypi.org/project/dagoptimizer/](https://pypi.org/project/dagoptimizer/)

Check:
- ✅ README renders correctly
- ✅ Version is correct
- ✅ Links work
- ✅ Classifiers are correct
- ✅ Dependencies are listed

---

## Step 7: Test Production Installation

```bash
# Create fresh environment
python -m venv prod_test_env
source prod_test_env/bin/activate  # On Windows: prod_test_env\Scripts\activate

# Install from PyPI
pip install dagoptimizer

# Test
python -c "from dagoptimizer import DAGOptimizer; print('PyPI installation works!')"

# Test with example
python -c "
from dagoptimizer import DAGOptimizer
edges = [('A', 'B'), ('B', 'C'), ('A', 'C')]
opt = DAGOptimizer(edges)
opt.transitive_reduction()
print(f'Reduced from 3 to {opt.graph.number_of_edges()} edges!')
"

# Deactivate
deactivate
rm -rf prod_test_env
```

---

## Step 8: Post-Publication Tasks

### 8.1 Create GitHub Release

1. Go to: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/releases/new
2. Tag version: `v1.0.0`
3. Release title: `DAG Optimizer v1.0.0`
4. Description: Copy from `CHANGELOG.md`
5. Attach: `dist/dagoptimizer-1.0.0.tar.gz` and `.whl` files
6. Publish release

### 8.2 Update Repository Badges

Add to `README.md`:

```markdown
[![PyPI version](https://img.shields.io/pypi/v/dagoptimizer.svg)](https://pypi.org/project/dagoptimizer/)
[![Python versions](https://img.shields.io/pypi/pyversions/dagoptimizer.svg)](https://pypi.org/project/dagoptimizer/)
[![Downloads](https://pepy.tech/badge/dagoptimizer)](https://pepy.tech/project/dagoptimizer)
```

### 8.3 Announce Release

- Twitter/X: "🚀 Just published DAG Optimizer v1.0.0 on PyPI! Advanced DAG optimization with adaptive algorithms. pip install dagoptimizer"
- LinkedIn: Share with detailed post
- Reddit: r/Python, r/programming
- Hacker News: Show HN
- Dev.to: Write a blog post

### 8.4 Update Documentation

- Update Wiki with installation instructions
- Add version to documentation
- Update examples to use published package

---

## Common Issues and Solutions

### Issue 1: "HTTPError: 403 Forbidden"

**Problem**: Invalid API token or permissions

**Solution**:
```bash
# Regenerate API token on PyPI
# Update ~/.pypirc with new token
# Try again
```

### Issue 2: "Version already exists"

**Problem**: Can't re-upload same version

**Solution**:
```bash
# Increment version in setup.py, pyproject.toml, __init__.py
# Rebuild: python -m build
# Upload again
```

### Issue 3: "README not rendering"

**Problem**: Markdown syntax errors

**Solution**:
```bash
# Install readme_renderer
pip install readme-renderer[md]

# Check README
python -m readme_renderer README.md -o /tmp/README.html

# View in browser and fix errors
```

### Issue 4: "Missing dependencies"

**Problem**: Dependencies not in requirements.txt

**Solution**:
```bash
# Add to requirements.txt
# Rebuild and upload
```

---

## Continuous Deployment (GitHub Actions)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add PyPI token as secret:
1. Go to: https://github.com/SahilShrivastava-Dev/Optimisation_of_DAGs/settings/secrets/actions
2. Add secret: `PYPI_API_TOKEN`
3. Value: Your PyPI API token

Now publishing happens automatically on release!

---

## Checklist

Before publishing, verify:

- [ ] Version updated in `setup.py`, `pyproject.toml`, `__init__.py`
- [ ] `CHANGELOG.md` updated with release notes
- [ ] All tests passing (`pytest`)
- [ ] Code formatted (`black src/`)
- [ ] Linting passing (`flake8 src/`)
- [ ] Type checking passing (`mypy src/`)
- [ ] README is up-to-date
- [ ] LICENSE file present
- [ ] `requirements.txt` is accurate
- [ ] Built distributions (`python -m build`)
- [ ] Checked with `twine check dist/*`
- [ ] Tested locally
- [ ] Tested on TestPyPI
- [ ] Ready for production PyPI

---

## Quick Reference

```bash
# Full publication workflow
rm -rf build dist *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Then production
```

---

## Additional Resources

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **setuptools**: https://setuptools.pypa.io/

---

**You're all set! 🎉 Welcome to PyPI!**

