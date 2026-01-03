# Publishing DAG Optimizer to PyPI

Complete guide to publish `dagoptimizer` package so users can `pip install dagoptimizer`.

## Prerequisites

### 1. Create PyPI Account
1. Go to https://pypi.org/account/register/
2. Verify your email
3. **Optional but HIGHLY RECOMMENDED**: Set up 2FA (Two-Factor Authentication)

### 2. Create TestPyPI Account (for testing)
1. Go to https://test.pypi.org/account/register/
2. Verify your email

### 3. Create API Tokens

**PyPI (Production):**
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name it (e.g., "dagoptimizer-upload")
4. Scope: "Entire account" (for first upload) or "Project: dagoptimizer" (for updates)
5. **SAVE THE TOKEN** - you'll only see it once!

**TestPyPI (Testing):**
1. Go to https://test.pypi.org/manage/account/token/
2. Create token same way as above
3. **SAVE THE TOKEN**

### 4. Install Build Tools

```bash
pip install --upgrade pip
pip install --upgrade build twine
```

---

## Publishing Process

### Step 1: Test Locally First

```bash
# Install in development mode
pip install -e .

# Test import
python -c "from dagoptimizer import DAGOptimizer; print('Import successful!')"

# Run demo
cd scripts
python 01_quick_start_demo.py
```

### Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution packages
python -m build
```

This creates:
- `dist/dagoptimizer-1.0.0.tar.gz` (source distribution)
- `dist/dagoptimizer-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 3: Test Upload to TestPyPI (RECOMMENDED)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your TestPyPI API token>
```

Test installation from TestPyPI:
```bash
# Create test environment
python -m venv test_env
test_env\Scripts\activate  # Windows
# source test_env/bin/activate  # Linux/Mac

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dagoptimizer

# Test it
python -c "from dagoptimizer import DAGOptimizer; print('Success!')"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

### Step 4: Upload to PyPI (Production)

```bash
# Upload to real PyPI
python -m twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your PyPI API token>
```

### Step 5: Verify Installation

```bash
# Create fresh environment
python -m venv verify_env
verify_env\Scripts\activate  # Windows

# Install from PyPI
pip install dagoptimizer

# Test
python -c "from dagoptimizer import DAGOptimizer; print('Published successfully!')"

# Cleanup
deactivate
rm -rf verify_env
```

---

## Updating the Package

When you want to update (add features, fix bugs, etc.):

### 1. Update Your Code
Make any changes you want to `src/dagoptimizer/`

### 2. Update Version Number
Update version in **BOTH** files:

**setup.py:**
```python
version="1.0.1",  # Increment this
```

**pyproject.toml:**
```toml
version = "1.0.1"  # Increment this
```

### 3. Update CHANGELOG.md
Document what changed:
```markdown
## [1.0.1] - 2025-01-01
### Added
- New feature X

### Fixed
- Bug Y
```

### 4. Rebuild and Republish

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Build new version
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

### 5. Users Update
Users can now update with:
```bash
pip install --upgrade dagoptimizer
```

---

## Version Numbering Guide

Use **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **1.0.0 → 1.0.1**: Patch (bug fixes, small improvements)
- **1.0.0 → 1.1.0**: Minor (new features, backward compatible)
- **1.0.0 → 2.0.0**: Major (breaking changes, API changes)

Examples:
- Fixed a bug? → `1.0.0` to `1.0.1`
- Added new metric method? → `1.0.0` to `1.1.0`
- Changed API completely? → `1.0.0` to `2.0.0`

---

## Configuration File (Optional)

Create `~/.pypirc` to avoid entering credentials every time:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = <your-pypi-token>

[testpypi]
username = __token__
password = <your-testpypi-token>
```

**Security Note:** Keep this file secure! Consider using keyring instead for production.

---

## Troubleshooting

### "Package already exists" error
- You uploaded this version already
- Increment version number in both `setup.py` and `pyproject.toml`
- Rebuild and re-upload

### Import errors after installation
- Check package structure: `src/dagoptimizer/__init__.py` must exist
- Verify `__init__.py` exports `DAGOptimizer`
- Check dependencies in `requirements.txt`

### "No module named 'dagoptimizer'" after pip install
- Try: `pip install --force-reinstall dagoptimizer`
- Check: `pip show dagoptimizer` to verify installation
- Ensure you're in the right Python environment

### Twine authentication issues
- Make sure username is exactly `__token__` (with double underscores)
- Copy-paste token carefully (include `pypi-` prefix)
- Check you're using the correct token (PyPI vs TestPyPI)

---

## Quick Reference Commands

```bash
# One-time setup
pip install --upgrade build twine

# Every release
rm -rf dist/ build/ *.egg-info
python -m build
python -m twine upload --repository testpypi dist/*  # Test first
python -m twine upload dist/*                         # Then production

# Verify
pip install dagoptimizer
python -c "from dagoptimizer import DAGOptimizer"
```

---

## After Publishing

1. **GitHub Release**: Create a release tag matching the version
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. **Update README**: Verify installation instructions work
3. **Announce**: Share on social media, GitHub Discussions, etc.
4. **Monitor**: Check PyPI stats at https://pypi.org/project/dagoptimizer/

---

## Best Practices

✅ **Always test on TestPyPI first**  
✅ **Test installation in clean environment**  
✅ **Update version number for every release**  
✅ **Document changes in CHANGELOG.md**  
✅ **Tag releases in git**  
✅ **Keep API tokens secure**  
✅ **Use semantic versioning**  

---

## Need Help?

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/

**You're ready to publish! 🚀**

