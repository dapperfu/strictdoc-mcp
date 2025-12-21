# Makefile for StrictDoc MCP Server
# Follows .cursor/rules/ requirements

PROJECT_NAME := $(shell basename $(PWD))
VENV_NAME := venv_$(PROJECT_NAME)
PYTHON := ${VENV_NAME}/bin/python
PIP := ${VENV_NAME}/bin/pip
UV := uv
PYTHON_SRC := src/
PYTHON_FILES := $(shell find ${PYTHON_SRC} -name '*.py')
TEST_FILES := $(shell find tests/ -name '*.py')
PORT := 20423

# Default target
.PHONY: all
all: ${VENV_NAME} install

# Virtual environment target (file-based dependency)
${VENV_NAME}:
	python3 -mvenv ${VENV_NAME}

# Install dependencies using UV
.PHONY: install
install: ${VENV_NAME}
	${UV} pip install -e .

# Install development dependencies
.PHONY: install-dev
install-dev: ${VENV_NAME}
	${UV} pip install -e ".[dev]"

# Install package in editable mode
.PHONY: develop
develop: ${VENV_NAME} install-dev

# Format code with ruff
.PHONY: format
format: ${VENV_NAME} ${PYTHON_FILES}
	${VENV_NAME}/bin/ruff format ${PYTHON_SRC} tests/

# Check code with ruff
.PHONY: check
check: ${VENV_NAME} ${PYTHON_FILES}
	${VENV_NAME}/bin/ruff check ${PYTHON_SRC} tests/

# Lint with mypy
.PHONY: lint
lint: ${VENV_NAME} ${PYTHON_FILES}
	${VENV_NAME}/bin/mypy ${PYTHON_SRC}

# Run tests
.PHONY: test
test: ${VENV_NAME} ${TEST_FILES}
	${VENV_NAME}/bin/pytest tests/

# Run unit tests only
.PHONY: test-unit
test-unit: ${VENV_NAME} ${TEST_FILES}
	${VENV_NAME}/bin/pytest tests/unit/

# Run integration tests only
.PHONY: test-integration
test-integration: ${VENV_NAME} ${TEST_FILES}
	${VENV_NAME}/bin/pytest tests/integration/

# Run MCP server (for testing)
# Default port: 20423 (can be overridden: make run PORT=20424)
.PHONY: run
run: ${VENV_NAME}
	@echo "Starting StrictDoc MCP Server (PORT=${PORT})"
	PORT=${PORT} ${PYTHON} -m strictdoc_mcp.server

# Clean generated files and cache
.PHONY: clean
clean:
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete

# Clean everything including venv
.PHONY: clean-all
clean-all: clean
	rm -rf ${VENV_NAME}

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all          - Create venv and install dependencies"
	@echo "  install      - Install package dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  develop      - Install package in editable mode with dev dependencies"
	@echo "  format       - Format code with ruff"
	@echo "  check        - Check code with ruff"
	@echo "  lint         - Type check with mypy"
	@echo "  test         - Run all tests"
	@echo "  test-unit    - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  run          - Run MCP server (default PORT=${PORT}, override with PORT=NNNN)"
	@echo "  clean        - Remove generated files and cache"
	@echo "  clean-all    - Remove everything including venv"
	@echo "  help         - Show this help message"

