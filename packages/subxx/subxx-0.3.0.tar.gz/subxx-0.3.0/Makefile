# Makefile for subxx - Subtitle fetching toolkit
# Requires: Make for Windows, uv package manager
#
# Quick start:
#   make help       - Show all available commands
#   make install    - Install dependencies
#   make test       - Run all tests

.PHONY: help install install-dev install-api install-all test test-unit test-integration test-fast test-coverage clean version md

# Default target - show help
help:
	@echo ""
	@echo "subxx - Subtitle Fetching Toolkit"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make install          Install core dependencies (uv sync)"
	@echo "  make install-dev      Install with dev dependencies (pytest)"
	@echo "  make install-api      Install with API dependencies (fastapi, uvicorn)"
	@echo "  make install-all      Install all dependencies (dev + api)"
	@echo ""
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo "  make test-fast        Run tests (skip slow network tests)"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo ""
	@echo "  make version          Show subxx version"
	@echo "  make clean            Clean cache and temporary files"
	@echo "  make clean-all        Clean everything including .venv"
	@echo ""
	@echo "  make list             List available subtitles for VIDEO_URL"
	@echo "  make subs             Download subtitles for VIDEO_URL"
	@echo "  make md               Download and extract to Markdown (VIDEO_ID only)"
	@echo ""
	@echo "Examples:"
	@echo "  make test-unit"
	@echo "  make test-coverage"
	@echo "  make subs VIDEO_URL=https://youtu.be/dQw4w9WgXcQ"
	@echo "  make md VIDEO_ID=dQw4w9WgXcQ"
	@echo ""

# Installation targets
install:
	@echo "Installing core dependencies..."
	uv sync

install-dev:
	@echo "Installing with dev dependencies (pytest, coverage)..."
	uv sync --extra dev

install-api:
	@echo "Installing with API dependencies (fastapi, uvicorn)..."
	uv sync --extra api

install-all:
	@echo "Installing all dependencies (dev + api)..."
	uv sync --extra dev --extra api

# Testing targets
test: install-dev
	@echo "Running all tests..."
	uv run pytest test_subxx.py -v

test-unit: install-dev
	@echo "Running unit tests only..."
	uv run pytest test_subxx.py -v -m unit

test-integration: install-dev
	@echo "Running integration tests only..."
	uv run pytest test_subxx.py -v -m integration

test-fast: install-dev
	@echo "Running tests (skipping slow network tests)..."
	uv run pytest test_subxx.py -v -m "not slow"

test-coverage: install-dev
	@echo "Running tests with coverage report..."
	uv run pytest test_subxx.py --cov=subxx --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

test-verbose: install-dev
	@echo "Running tests with verbose output..."
	uv run pytest test_subxx.py -vv -s

# Application commands (once implemented)
version:
	@echo "Checking subxx version..."
	@uv run python __main__.py version || echo "Implementation not yet complete"

list:
ifndef VIDEO_URL
	@echo "Error: VIDEO_URL not specified"
	@echo "Usage: make list VIDEO_URL=https://youtu.be/VIDEO_ID"
	@exit 1
endif
	@echo "Listing subtitles for $(VIDEO_URL)..."
	@uv run python __main__.py list $(VIDEO_URL) || echo "Implementation not yet complete"

subs:
ifndef VIDEO_URL
	@echo "Error: VIDEO_URL not specified"
	@echo "Usage: make subs VIDEO_URL=https://youtu.be/VIDEO_ID"
	@echo "Optional: LANGS=en,de OUTPUT_DIR=./subs"
	@exit 1
endif
	@echo "Downloading subtitles for $(VIDEO_URL)..."
ifdef LANGS
	@uv run python __main__.py subs $(VIDEO_URL) --langs $(LANGS) || echo "Implementation not yet complete"
else
	@uv run python __main__.py subs $(VIDEO_URL) || echo "Implementation not yet complete"
endif

md:
ifndef VIDEO_ID
	@echo "Error: VIDEO_ID not specified"
	@echo "Usage: make md VIDEO_ID=dQw4w9WgXcQ"
	@echo "Optional: TIMESTAMPS=300 (for 5-minute intervals)"
	@exit 1
endif
	@echo "Downloading and extracting to Markdown for video ID: $(VIDEO_ID)..."
ifdef TIMESTAMPS
	@uv run python __main__.py subs https://youtu.be/$(VIDEO_ID) --md --timestamps $(TIMESTAMPS) --force
else
	@uv run python __main__.py subs https://youtu.be/$(VIDEO_ID) --md --force
endif

# Cleaning targets
clean:
	@echo "Cleaning cache and temporary files..."
	-@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
	-@if exist htmlcov rmdir /s /q htmlcov 2>nul
	-@if exist .coverage del /f .coverage 2>nul
	-@if exist *.pyc del /f *.pyc 2>nul
	-@for /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i" 2>nul
	@echo "Clean complete."

clean-all: clean
	@echo "Removing virtual environment..."
	-@if exist .venv rmdir /s /q .venv 2>nul
	-@if exist uv.lock del /f uv.lock 2>nul
	@echo "All clean."

# Development helpers
check-uv:
	@where uv >nul 2>&1 || (echo "Error: uv not found. Install from https://github.com/astral-sh/uv" && exit 1)
	@echo "uv package manager is installed"

check-make:
	@echo "Make for Windows is installed and working"

# Info target
info:
	@echo ""
	@echo "Project Information"
	@echo "==================="
	@echo ""
	@echo "Project: subxx"
	@echo "Version: 0.1.0"
	@echo "Description: Subtitle fetching toolkit"
	@echo ""
	@echo "Dependencies:"
	@uv tree 2>nul || echo "Run 'make install' first"
	@echo ""
