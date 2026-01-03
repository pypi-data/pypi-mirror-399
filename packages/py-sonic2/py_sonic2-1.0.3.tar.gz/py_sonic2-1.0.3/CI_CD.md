# CI/CD Configuration Guide

This document explains the GitLab CI/CD pipeline for py-sonic2.

## Pipeline Overview

The CI/CD pipeline consists of three stages:

1. **Test** - Code quality, testing, and security checks
2. **Build** - Package building and verification
3. **Publish** - Publishing to PyPI repositories

## Pipeline Stages

### Stage 1: Test

#### Lint Job
- Runs code quality checks using `ruff`
- Executes on: merge requests, main/master branches
- Failure: Non-blocking (allows pipeline to continue)

#### Test Job
- Runs tests across Python versions 3.8-3.13 in parallel
- Generates coverage reports (XML and HTML)
- Executes on: merge requests, main/master branches
- Currently placeholder - add pytest tests to enable
- Coverage reports available as artifacts for 30 days

#### Security Job
- Runs `safety` to check for vulnerable dependencies
- Runs `bandit` to scan for security issues in code
- Executes on: merge requests, main/master branches
- Failure: Non-blocking (warnings only)

#### Dependency Check Job
- Uses `pip-audit` to find vulnerable dependencies
- Executes on: scheduled pipelines, main/master branches
- Failure: Non-blocking (warnings only)

### Stage 2: Build

#### Build Job
- Cleans previous builds
- Builds source distribution (.tar.gz) and wheel (.whl)
- Verifies package with twine
- Stores build artifacts for 7 days
- Executes on: merge requests, main/master branches, tags

### Stage 3: Publish

#### TestPyPI Job
- Publishes to TestPyPI (test.pypi.org)
- Executes on: main/master branches
- **Manual trigger required** (when: manual)
- Requires: Build job artifacts
- Environment: testpypi

#### PyPI Job
- Publishes to production PyPI (pypi.org)
- Executes on: tags only
- **Manual trigger required** (when: manual)
- Requires: Build job artifacts
- Environment: production

## Required GitLab CI/CD Variables

To enable publishing to PyPI, configure these variables in GitLab:

**Settings → CI/CD → Variables**

### For TestPyPI:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `TWINE_USERNAME` | `__token__` | ✓ | ✗ |
| `TWINE_PASSWORD` | `pypi-...` (TestPyPI token) | ✓ | ✓ |
| `TWINE_REPOSITORY_URL` | `https://test.pypi.org/legacy/` | ✗ | ✗ |

### For Production PyPI:

| Variable | Value | Protected | Masked |
|----------|-------|-----------|--------|
| `TWINE_USERNAME` | `__token__` | ✓ | ✗ |
| `TWINE_PASSWORD` | `pypi-...` (PyPI token) | ✓ | ✓ |

**Note:** You can use different tokens for TestPyPI and PyPI by setting environment-specific variables.

## How to Get PyPI Tokens

### TestPyPI Token:
1. Create account at https://test.pypi.org/account/register/
2. Go to https://test.pypi.org/manage/account/token/
3. Click "Add API token"
4. Set scope to "Entire account" or "py-sonic2" project
5. Copy the token (starts with `pypi-`)

### Production PyPI Token:
1. Create account at https://pypi.org/account/register/
2. Go to https://pypi.org/manage/account/token/
3. Click "Add API token"
4. Set scope to "Entire account" or "py-sonic2" project
5. Copy the token (starts with `pypi-`)

## Usage Workflows

### Development Workflow

1. **Create a branch** for your feature/fix
2. **Push commits** - Pipeline runs lint, test, security, and build jobs
3. **Create merge request** - All checks run automatically
4. **Merge to main/master** - Full pipeline runs, ready for TestPyPI

### Release Workflow

#### Step 1: Test on TestPyPI
```bash
# 1. Update version in libsonic/__init__.py
vim libsonic/__init__.py  # Change __version__

# 2. Commit and push to main/master
git add libsonic/__init__.py
git commit -m "Bump version to X.Y.Z"
git push origin main

# 3. In GitLab UI:
#    - Go to CI/CD → Pipelines
#    - Find the pipeline for your commit
#    - Manually trigger "publish:testpypi" job

# 4. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps py-sonic2
```

#### Step 2: Release to Production PyPI
```bash
# 1. Create and push a git tag
git tag -a v1.0.4 -m "Release version 1.0.4"
git push origin v1.0.4

# 2. In GitLab UI:
#    - Go to CI/CD → Pipelines
#    - Find the pipeline for your tag
#    - Manually trigger "publish:pypi" job

# 3. Verify on PyPI
# Visit https://pypi.org/project/py-sonic2/
```

## Pipeline Optimization

### Caching
The pipeline caches:
- `pip` packages in `.cache/pip`
- `uv` cache in `.cache/uv`
- Virtual environment in `.venv/`

This speeds up subsequent pipeline runs.

### Parallel Execution
- Tests run in parallel across 6 Python versions
- Reduces total pipeline time significantly

### Artifacts
- Test coverage reports: 30 days
- Build distributions: 7 days
- Coverage HTML reports: 30 days

## Troubleshooting

### Publishing Fails with Authentication Error
- Verify `TWINE_USERNAME` is set to `__token__`
- Verify `TWINE_PASSWORD` contains the full token (including `pypi-` prefix)
- Check token hasn't expired or been revoked
- Ensure variables are marked as "Masked" for security

### Build Fails
- Check that all required files exist (setup.py, pyproject.toml, etc.)
- Verify version string in `libsonic/__init__.py` is valid
- Review build logs for specific error messages

### Tests Fail
- Currently tests are placeholder - add actual pytest tests
- Check Python version compatibility
- Review test output in pipeline logs

### Package Already Exists on PyPI
- PyPI doesn't allow re-uploading the same version
- Bump version in `libsonic/__init__.py`
- Create new tag and re-run pipeline

## Security Best Practices

1. **Never commit tokens** to the repository
2. **Use masked variables** for all secrets in GitLab
3. **Use protected variables** for production tokens
4. **Use project-scoped tokens** when possible
5. **Rotate tokens** periodically
6. **Review security job** warnings regularly

## Scheduled Pipelines

Consider setting up scheduled pipelines for:
- **Daily dependency checks** - Catch vulnerable dependencies early
- **Weekly test runs** - Ensure compatibility with latest Python versions
- **Monthly security audits** - Full security scan

Configure in: **CI/CD → Schedules**

## Adding Tests

To enable the test job, create tests using pytest:

```bash
# Create tests directory
mkdir tests
touch tests/__init__.py
touch tests/test_connection.py

# Add pytest to dependencies
uv add --dev pytest pytest-cov

# Write tests
# tests/test_connection.py
def test_connection():
    from libsonic import Connection
    # Add actual tests here
    assert True
```

Then uncomment the pytest line in `.gitlab-ci.yml`:
```yaml
- uv run pytest tests/ --cov=libsonic --cov-report=xml --cov-report=html
```

## Monitoring

Monitor your pipelines:
- **CI/CD → Pipelines** - View all pipeline runs
- **CI/CD → Jobs** - View individual job details
- **Deployments → Environments** - Track TestPyPI and PyPI deployments

## Additional Resources

- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
