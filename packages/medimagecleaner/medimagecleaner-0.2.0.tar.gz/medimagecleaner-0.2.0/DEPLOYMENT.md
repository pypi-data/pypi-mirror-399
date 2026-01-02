# PyPI Deployment Guide for medimagecleaner

This guide walks you through deploying the medimagecleaner package to PyPI using Twine.

## Prerequisites

1. **Python 3.8+** installed
2. **pip** and **setuptools** up to date
3. **PyPI account** (create at https://pypi.org/account/register/)
4. **Test PyPI account** (optional, create at https://test.pypi.org/account/register/)

## Step 1: Install Build Tools

```bash
pip install --upgrade pip setuptools wheel twine build
```

## Step 2: Prepare Package

### 2.1 Verify Package Structure

Ensure your directory structure looks like this:

```
medimagecleaner/
├── medimagecleaner/
│   ├── __init__.py
│   ├── dicom_deidentifier.py
│   ├── text_remover.py
│   ├── format_converter.py
│   ├── validator.py
│   ├── audit_logger.py
│   ├── batch_processor.py
│   ├── face_remover.py
│   ├── risk_assessment.py
│   ├── progress.py
│   └── cli.py
├── examples/
│   ├── complete_example.py
│   └── advanced_features_example.py
├── setup.py
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── LICENSE
├── requirements.txt
└── DEPLOYMENT.md (this file)
```

### 2.2 Update Version Number

Before each release, update version in:
- `setup.py` (line with `version=`)
- `pyproject.toml` (line with `version =`)
- `medimagecleaner/__init__.py` (line with `__version__ =`)

## Step 3: Build Distribution Packages

### 3.1 Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info

# Or on Windows
rmdir /s /q build dist
del /s /q *.egg-info
```

### 3.2 Build the Package

```bash
# Using modern build tool (recommended)
python -m build

# Or using setup.py (older method)
python setup.py sdist bdist_wheel
```

This creates:
- `dist/medimagecleaner-0.2.0.tar.gz` (source distribution)
- `dist/medimagecleaner-0.2.0-py3-none-any.whl` (wheel distribution)

### 3.3 Verify Build

```bash
# Check the contents
tar -tzf dist/medimagecleaner-0.2.0.tar.gz

# On Windows, use 7-Zip or similar to inspect the .tar.gz file
```

## Step 4: Configure PyPI Credentials

### 4.1 Generate API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Name: `medimagecleaner-upload`
4. Scope: Select "Entire account" or specific project
5. Copy the token (starts with `pypi-`)

### 4.2 Create .pypirc File

Create `~/.pypirc` (Linux/Mac) or `%USERPROFILE%\.pypirc` (Windows):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_ACTUAL_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Security Note**: Keep this file secure! Never commit it to version control.

## Step 5: Test on Test PyPI (Recommended)

### 5.1 Upload to Test PyPI

```bash
twine upload --repository testpypi dist/*
```

### 5.2 Test Installation

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ medimagecleaner

# Test the package
python -c "import medimagecleaner; print(medimagecleaner.__version__)"
medimagecleaner --help

# Clean up
deactivate
rm -rf test_env
```

## Step 6: Upload to PyPI

### 6.1 Final Checks

- [ ] Version number updated in all files
- [ ] README.md is complete and accurate
- [ ] LICENSE file is present
- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] Changelog is updated

### 6.2 Upload to PyPI

```bash
twine upload dist/*
```

You'll see output like:

```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading medimagecleaner-0.2.0-py3-none-any.whl
100%|████████████████████| 45.2k/45.2k [00:01<00:00, 32.1kB/s]
Uploading medimagecleaner-0.2.0.tar.gz
100%|████████████████████| 42.3k/42.3k [00:00<00:00, 48.5kB/s]

View at:
https://pypi.org/project/medimagecleaner/0.2.0/
```

### 6.3 Verify Upload

1. Visit https://pypi.org/project/medimagecleaner/
2. Check that version 0.2.0 is listed
3. Verify README displays correctly
4. Check links and badges work

## Step 7: Test Installation from PyPI

```bash
# Create fresh environment
python -m venv verify_env
source verify_env/bin/activate  # Windows: verify_env\Scripts\activate

# Install from PyPI
pip install medimagecleaner

# Test installation
python -c "import medimagecleaner; print(medimagecleaner.__version__)"
medimagecleaner --version

# Test with OCR extras
pip install medimagecleaner[ocr]

# Clean up
deactivate
rm -rf verify_env
```

## Step 8: Post-Release Tasks

### 8.1 Create Git Tag

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 8.2 Create GitHub Release

1. Go to GitHub repository releases
2. Click "Create a new release"
3. Tag: v0.2.0
4. Title: medimagecleaner v0.2.0
5. Description: Copy changelog from README
6. Attach: dist/medimagecleaner-0.2.0.tar.gz

### 8.3 Update Documentation

- [ ] Update main README if needed
- [ ] Update documentation site (if applicable)
- [ ] Announce on relevant channels

## Troubleshooting

### Issue: Upload fails with authentication error

**Solution**: 
```bash
# Re-generate API token on PyPI
# Update ~/.pypirc with new token
# Try upload again
```

### Issue: "File already exists" error

**Solution**: 
```bash
# You cannot re-upload the same version
# Increment version number in setup.py, pyproject.toml, and __init__.py
# Rebuild and upload
```

### Issue: README not displaying on PyPI

**Solution**:
```bash
# Verify README.md is valid Markdown
# Check long_description_content_type in setup.py
# Ensure README.md is included in MANIFEST.in
```

### Issue: Missing files in distribution

**Solution**:
```bash
# Check MANIFEST.in includes all necessary files
# Verify files are tracked by git
# Rebuild the distribution
```

## Quick Reference Commands

```bash
# Complete deployment workflow
rm -rf build/ dist/ *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*  # Test first
twine upload dist/*                         # Production

# Install and test
pip install medimagecleaner
python -c "import medimagecleaner; print(medimagecleaner.__version__)"
```

## Security Best Practices

1. **Use API tokens** instead of username/password
2. **Limit token scope** to specific projects when possible
3. **Rotate tokens** periodically
4. **Never commit** .pypirc to version control
5. **Use environment variables** in CI/CD pipelines
6. **Enable 2FA** on your PyPI account

## CI/CD Integration (GitHub Actions Example)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
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

## Resources

- **PyPI Documentation**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/
- **Python Packaging Guide**: https://packaging.python.org/guides/
- **setuptools Documentation**: https://setuptools.pypa.io/

## Support

For deployment issues:
- PyPI Help: https://pypi.org/help/
- Python Packaging Discord: https://discord.gg/pypa
- Stack Overflow: Tag `python-packaging`

---

**Last Updated**: December 28, 2025  
**Package Version**: 0.2.0
