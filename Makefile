SHELL := /bin/bash

.PHONY: setup
setup: venv lint test-unit

.PHONY: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

.PHONY: clean-test
clean-test:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf .reports
	rm -rf htmlcov/
	rm -rf .pytest_cache

.PHONY: clean
clean: clean-pyc clean-test

venv: poetry.lock
	poetry install

.PHONY: format
format: venv
	poetry run black nodestream tests
	poetry run isort nodestream tests

.PHONY: lint
lint: venv
	poetry run black nodestream tests --check
	poetry run ruff nodestream tests

.PHONY: test-unit
test-unit: venv
	poetry run pytest