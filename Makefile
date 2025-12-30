.PHONY: help install install-dev test lint format validate-scenarios demo clean

help:  ## Show this help message
	@echo "ParentingBench - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ -v --cov=parentingbench --cov-report=term --cov-report=html

lint:  ## Run linting checks
	ruff check parentingbench tests scripts
	black --check parentingbench tests scripts --line-length 100

format:  ## Format code with black
	black parentingbench tests scripts --line-length 100

validate-scenarios:  ## Validate all scenario files
	PYTHONPATH=. python scripts/validate_scenarios.py parentingbench/scenarios/**/*.yaml

demo:  ## Run demo script
	python demo_usage.py

clean:  ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/ .coverage coverage.xml

# Evaluation commands
evaluate-example:  ## Run example evaluation with gpt-4
	python -m parentingbench.evaluate \
		--model gpt-4 \
		--scenario parentingbench/scenarios/school_age/emotional_mental_health_anxiety_school.yaml \
		--verbose

compare-example:  ## Run example comparison between models
	python -m parentingbench.compare \
		--models gpt-4 claude-3-5-sonnet-20241022 \
		--output results/comparison

# CI/CD commands
ci-test:  ## Run CI tests locally
	pytest tests/ -v --cov=parentingbench --cov-report=xml

ci-lint:  ## Run CI linting locally
	black --check parentingbench tests scripts --line-length 100
	ruff check parentingbench tests scripts
