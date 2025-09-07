# Trello Sprint Generator - Development Makefile

.PHONY: help install install-dev test test-cov lint format clean run-example

help: ## Show this help message
	@echo "Trello Sprint Generator - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

run-example: ## Run example with the sample sprint file
	python main.py --file examples/example_sprint.md --board-id Z0OpcpxE --dry-run

test-connection: ## Test connection to Trello API
	python main.py --test-connection

build: ## Build the package
	python setup.py sdist bdist_wheel

install-package: ## Install the package in development mode
	pip install -e .

check: lint test ## Run all checks (lint + test)
