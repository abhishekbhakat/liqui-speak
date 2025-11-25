.PHONY: install install-dev lint format type-check test clean build

# Install the package
install:
	uv pip install -e .

# Install with dev dependencies
install-dev:
	uv pip install -e ".[dev]"

# Run linting
lint:
	ruff check src tests
	flake8 src tests

# Format code
format:
	ruff format src tests
	black src tests

# Type checking
type-check:
	pyright

# Run tests
test:
	pytest

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	uv build

# Install system dependencies
install-system-deps:
	@echo "Installing system dependencies..."
	@echo "Please run the appropriate command for your system:"
	@echo "  macOS: brew install portaudio ffmpeg"
	@echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev ffmpeg"
	@echo "  CentOS/RHEL: sudo yum install portaudio-devel ffmpeg"
	@echo "  Arch: sudo pacman -S portaudio ffmpeg"
	@echo "  Windows (with Chocolatey): choco install portaudio ffmpeg"

# Quick development setup
dev-setup: install-dev
	@echo "Development environment ready!"
	@echo "Run 'make lint' to check code quality"
	@echo "Run 'make test' to run tests"

# Full quality check
quality: lint type-check test
	@echo "All quality checks passed!"