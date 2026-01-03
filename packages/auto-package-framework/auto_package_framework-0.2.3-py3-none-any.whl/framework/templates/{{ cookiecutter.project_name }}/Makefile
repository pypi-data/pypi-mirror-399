.PHONY: help install install-dev format lint type-check test test-cov clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install package
	pip install -e .

install-dev: ## Install package with dev dependencies
	pip install -e ".[dev]"
	pre-commit install

format: ## Format code with ruff
	ruff format .

lint: ## Lint code with ruff
	ruff check .

type-check: ## Type check with mypy
	mypy . --ignore-missing-imports || true

check: format lint type-check ## Run all checks (format, lint, type-check)

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	pytest-watch

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	python -m build

publish-test: build ## Publish to TestPyPI
	python -m twine upload --repository testpypi dist/*

publish: build ## Publish to PyPI
	python -m twine upload dist/*

pre-commit: ## Run pre-commit on all files
	pre-commit run --all-files

all: check test ## Run all checks and tests


