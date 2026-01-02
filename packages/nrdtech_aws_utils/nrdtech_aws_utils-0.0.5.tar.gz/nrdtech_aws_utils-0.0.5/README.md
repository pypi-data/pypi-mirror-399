# NRD Tech AWS Python Utils

## Description
A library of helpful wrappers around boto3 aws functions

## Testing
```
pytest
```

```
pytest --cov=nrdtech_aws_utils tests/
```

## Build
```
python -m pip install --upgrade pip
pip install flit
flit build
```

## Publishing to PyPI

### Prerequisites
1. Create an account on [PyPI](https://pypi.org/account/register/) (for production) and/or [TestPyPI](https://test.pypi.org/account/register/) (for testing)
2. Create an API token:
   - Go to Account Settings → API tokens
   - Create a new token with appropriate scope (project or account)
   - Save the token (you'll only see it once)

### Option 1: Using flit (recommended)
```bash
# Install flit if not already installed
pip install flit

# Build the package
flit build

# Publish to TestPyPI (for testing)
flit publish --repository testpypi

# Publish to PyPI (production)
flit publish
```

### Option 2: Using twine (alternative)
```bash
# Install twine
pip install twine

# Build the package (if not already built)
flit build

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

### First-time setup
When publishing for the first time, you'll be prompted for:
- **Username**: `__token__` (literally, with underscores)
- **Password**: Your API token (starts with `pypi-`)

### Testing before production
Always test on TestPyPI first:
```bash
# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ nrdtech-aws-utils
```

### Notes
- Make sure to increment the version in `pyproject.toml` before each release
- The package name on PyPI will be `nrdtech-aws-utils` (hyphens, not underscores)
- After publishing, it may take a few minutes for the package to be available
