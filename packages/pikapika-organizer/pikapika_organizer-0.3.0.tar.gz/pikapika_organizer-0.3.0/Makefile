.PHONY: help test check format format-check install dev-install run clean release-patch release-minor release-major release-dry

# Default target
help:
	@echo "Available commands:"
	@echo "  test          - Run tests"
	@echo "  check         - Run ruff linting checks"
	@echo "  format        - Format code with ruff"
	@echo "  format-check  - Check if code is formatted"
	@echo "  install       - Install the package"
	@echo "  dev-install   - Install with dev dependencies"
	@echo "  run           - Run the pikapika CLI"
	@echo "  clean         - Clean cache files"
	@echo "  release-patch - Create patch release (x.y.Z)"
	@echo "  release-minor - Create minor release (x.Y.z)"
	@echo "  release-major - Create major release (X.y.z)"
	@echo "  release-dry   - Preview release without making changes"

# Run tests
test:
	uv run python -m pytest

# Run linting checks
check:
	uv run ruff check

# Format code
format:
	uv run ruff format

# Check formatting without changing files
format-check:
	uv run ruff format --check

# Install the package
install:
	uv sync

# Install with dev dependencies
dev-install:
	uv sync --group dev

# Run the CLI
run:
	uv run pikapika

# Clean cache and build artifacts
clean:
	@echo "Cleaning cache files..."
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf *.egg-info
	@rm -rf build
	@rm -rf dist
	@echo "Done!"

# Release commands
release-patch:
	uv run python scripts/release.py patch

release-minor:
	uv run python scripts/release.py minor

release-major:
	uv run python scripts/release.py major

release-dry:
	uv run python scripts/release.py patch --dry-run