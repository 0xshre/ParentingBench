# ParentingBench Makefile

.PHONY: help install test lint format docs clean

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies including pre-commit
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=parentingbench --cov-report=html

lint:  ## Run linters (black, isort, mypy)
	black --check parentingbench/ tests/
	isort --check-only --profile black parentingbench/ tests/
	mypy parentingbench/

format:  ## Auto-format code
	black parentingbench/ tests/
	isort --profile black parentingbench/ tests/

docs:  ## Update documentation (project structure in README)
	python scripts/update_docs.py

demo:  ## Run demo scripts
	@echo "Running basic demo..."
	python demo_usage.py
	@echo ""
	@echo "Running comparison demo..."
	python demo_comparison.py

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage
	rm -rf results/

# Build targets
build: format lint test docs  ## Run full build process (format, lint, test, docs)
	@echo "✅ Build complete!"

ci: lint test docs  ## Run CI checks (lint, test, docs) - no formatting
	@echo "✅ CI checks passed!"

# Evaluation targets
evaluate-gpt4:  ## Evaluate GPT-4 on all scenarios
	python -m parentingbench.evaluate \
		--model gpt-4 \
		--scenarios-dir parentingbench/scenarios \
		--output results/gpt4.json

evaluate-claude:  ## Evaluate Claude on all scenarios
	python -m parentingbench.evaluate \
		--model claude-3-5-sonnet-20241022 \
		--scenarios-dir parentingbench/scenarios \
		--output results/claude.json

compare:  ## Compare GPT-4 vs Claude
	python -m parentingbench.compare \
		--models gpt-4 claude-3-5-sonnet-20241022 \
		--output results/comparison
