.PHONY: help clean build check install install-dev test upload upload-test version

# Default target
help:
	@echo "py-sonic2 - Makefile commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make clean        - Remove build artifacts and cache files"
	@echo "  make build        - Build source and wheel distributions"
	@echo "  make check        - Verify package with twine"
	@echo "  make install      - Install package locally"
	@echo "  make install-dev  - Install package in development mode with dev dependencies"
	@echo "  make test         - Run tests (placeholder - add when tests exist)"
	@echo "  make upload-test  - Upload to TestPyPI"
	@echo "  make upload       - Upload to PyPI (production)"
	@echo "  make version      - Show current package version"
	@echo "  make release      - Full release workflow: clean, build, check, upload"
	@echo ""

# Remove all build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf py_sonic2.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	@echo "✓ Clean complete"

# Build the package
build: clean
	@echo "Building package..."
	uv run python -m build
	@echo "✓ Build complete"
	@echo ""
	@ls -lh dist/

# Check package with twine
check: build
	@echo "Checking package with twine..."
	uv run python -m twine check dist/*
	@echo "✓ Package check complete"

# Install package locally
install:
	@echo "Installing package..."
	uv pip install .
	@echo "✓ Installation complete"

# Install in development mode with dev dependencies
install-dev:
	@echo "Installing package in development mode..."
	uv pip install -e .
	uv add --dev build twine
	@echo "✓ Development installation complete"

# Run tests (placeholder)
test:
	@echo "Running tests..."
	@echo "⚠ No tests configured yet. Add pytest and tests to use this target."
	# uv run pytest tests/

# Get current version
version:
	@grep "__version__" libsonic/__init__.py | sed "s/__version__ = /Current version: /" | tr -d "'"

# Upload to TestPyPI
upload-test: check
	@echo "Uploading to TestPyPI..."
	@echo "⚠ Make sure you have configured ~/.pypirc with TestPyPI credentials"
	uv run python -m twine upload --repository testpypi dist/*
	@echo "✓ Upload to TestPyPI complete"
	@echo ""
	@echo "Test installation with:"
	@echo "  pip install --index-url https://test.pypi.org/simple/ --no-deps py-sonic2"

# Upload to PyPI (production)
upload: check
	@echo "⚠ WARNING: You are about to upload to PRODUCTION PyPI!"
	@echo "⚠ This action cannot be undone for this version number."
	@echo ""
	@read -p "Are you sure you want to continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "Uploading to PyPI..."; \
		uv run python -m twine upload dist/*; \
		echo "✓ Upload to PyPI complete"; \
		echo ""; \
		echo "View your package at: https://pypi.org/project/py-sonic2/"; \
	else \
		echo "Upload cancelled."; \
		exit 1; \
	fi

# Full release workflow
release: version
	@echo "Starting release workflow..."
	@echo ""
	@$(MAKE) clean
	@echo ""
	@$(MAKE) build
	@echo ""
	@$(MAKE) check
	@echo ""
	@echo "✓ Release preparation complete"
	@echo ""
	@echo "Package is ready for upload!"
	@echo "Run 'make upload-test' to test on TestPyPI first"
	@echo "Run 'make upload' to publish to PyPI"
