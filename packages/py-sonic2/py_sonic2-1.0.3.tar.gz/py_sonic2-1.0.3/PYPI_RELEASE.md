# PyPI Release Guide

This guide explains how to build and publish py-sonic2 to PyPI.

## Quick Start (Using Makefile)

The easiest way to build and publish is using the included Makefile:

```bash
# View all available commands
make help

# Full release workflow (clean, build, check)
make release

# Upload to TestPyPI (recommended first step)
make upload-test

# Upload to production PyPI
make upload
```

## Manual Process

If you prefer to run commands manually, follow the steps below.

## Prerequisites

1. Install build tools:
```bash
pip install --upgrade build twine
```

2. Create a PyPI account at https://pypi.org/account/register/

3. Generate an API token:
   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Give it a descriptive name (e.g., "py-sonic2-upload")
   - Set the scope (can be "Entire account" or specific to this project)
   - Copy the token (starts with `pypi-`)

4. Configure PyPI credentials:
   - Copy `.pypirc.template` to `~/.pypirc`
   - Replace `pypi-YOUR_API_TOKEN_HERE` with your actual token
   - Set appropriate permissions: `chmod 600 ~/.pypirc`

## Building the Package

1. Clean up any previous builds:
```bash
rm -rf build/ dist/ *.egg-info
```

2. Build the distribution packages:
```bash
python -m build
```

This creates:
- `dist/py-sonic2-X.Y.Z-py3-none-any.whl` (wheel distribution)
- `dist/py-sonic2-X.Y.Z.tar.gz` (source distribution)

## Testing the Build (Optional but Recommended)

Test your package on TestPyPI first:

1. Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

2. Install from TestPyPI to verify:
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps py-sonic2
```

3. Test that the package works as expected.

## Publishing to PyPI

1. Check the package for common errors:
```bash
python -m twine check dist/*
```

2. Upload to PyPI:
```bash
python -m twine upload dist/*
```

3. Verify the upload at https://pypi.org/project/py-sonic2/

## Post-Release Steps

1. Tag the release in git:
```bash
git tag -a v1.0.3 -m "Release version 1.0.3"
git push origin v1.0.3
```

2. Create a GitHub release with release notes

3. Test installation:
```bash
pip install py-sonic2
```

## Version Bumping

Before each release, update the version number in:
- `libsonic/__init__.py` (change `__version__`)

The version will be automatically picked up by both `setup.py` and `pyproject.toml`.

## Troubleshooting

### Authentication Errors
- Verify your API token is correct in `~/.pypirc`
- Ensure you're using `__token__` as the username, not your PyPI username

### Package Already Exists
- PyPI does not allow re-uploading the same version
- Bump the version number in `libsonic/__init__.py` and rebuild

### Import Errors After Installation
- Check that `MANIFEST.in` includes all necessary files
- Verify `libsonic/__init__.py` properly exports the Connection class

### Missing README on PyPI
- Ensure README.md is included in MANIFEST.in
- Check that `long_description_content_type="text/markdown"` is set in setup.py

## Security Notes

- Never commit `.pypirc` or API tokens to git
- The `.gitignore` should include `.pypirc`
- API tokens can be revoked and regenerated at https://pypi.org/manage/account/token/
- Use project-scoped tokens when possible for better security
