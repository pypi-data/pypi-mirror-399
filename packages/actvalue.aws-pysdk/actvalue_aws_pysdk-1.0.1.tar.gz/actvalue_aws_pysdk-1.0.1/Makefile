.PHONY: help install test lint format build publish publish-test clean venv

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies with uv"
	@echo "  make test         - Run tests with pytest"
	@echo "  make lint         - Lint code with ruff"
	@echo "  make format       - Format code with ruff"
	@echo "  make build        - Build package with uv"
	@echo "  make publish      - Publish to PyPI"
	@echo "  make publish-test - Publish to Test PyPI"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make venv         - Show virtual environment location"

install:
	@echo "Setting up Python environment with uv..."
	uv sync --all-extras --all-groups
	@echo "Virtual environment created at .venv/"

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

format:
	uv run ruff format src tests

build:
	uv build

publish:
	uv run twine upload dist/*

publish-test:
	uv run twine upload --repository testpypi dist/*

venv:
	@echo "Virtual environment location:"
	@uv run python -c "import sys; print(sys.prefix)"

clean:
	rm -rf dist .pytest_cache src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
