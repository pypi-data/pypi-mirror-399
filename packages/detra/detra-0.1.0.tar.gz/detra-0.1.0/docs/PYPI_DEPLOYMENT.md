# PyPI Deployment Guide

Quick guide to deploy `detra` to PyPI.

## Prerequisites

- PyPI and TestPyPI accounts (already created)
- API tokens for both (get from account settings)
- Build tools installed: `pip install build twine`

## Deployment Steps

### 1. Update Version

Update version in both files:
- `pyproject.toml`: `version = "0.1.0"`
- `src/detra/__init__.py`: `__version__ = "0.1.0"`

### 2. Test on TestPyPI

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: <your-testpypi-api-token>
```

### 3. Test Installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ detra
python -c "import detra; print(detra.__version__)"
```

### 4. Deploy to PyPI

```bash
# Clean and build
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*

# Upload to PyPI
twine upload dist/*

# When prompted:
# Username: __token__
# Password: <your-pypi-api-token>
```

### 5. Verify

- Visit: https://pypi.org/project/detra/
- Test install: `pip install detra`

## Updating for New Releases

1. Update version numbers (both files)
2. Commit changes
3. Create git tag: `git tag v0.1.0 && git push origin v0.1.0`
4. Build and upload (steps 2-4 above)

## Notes

- Versions cannot be reused once published
- Always test on TestPyPI first
- Use API tokens (not passwords) for authentication
