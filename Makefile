# BookBot Makefile
# Convenient commands for development and deployment

.PHONY: help install install-dev test lint format build docker docker-run clean

# Default target
help:
	@echo "BookBot Development Commands"
	@echo "============================"
	@echo ""
	@echo "  make install      Install dependencies"
	@echo "  make install-dev  Install with dev dependencies"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linting"
	@echo "  make format       Format code with Black"
	@echo "  make build        Build package"
	@echo "  make docker       Build Docker image"
	@echo "  make docker-run   Run in Docker"
	@echo "  make clean        Clean build artifacts"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e ".[all]"

# Testing
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=src/bookbot --cov-report=html --cov-report=term

# Linting
lint:
	flake8 src/ tests/ main.py --max-line-length=100
	mypy src/bookbot/ --ignore-missing-imports

format:
	black src/ tests/ main.py

format-check:
	black --check --diff src/ tests/ main.py

# Building
build:
	python -m build

build-clean: clean build

# Docker
docker:
	docker build -t bookbot:latest .

docker-run:
	docker run --rm -v $$(pwd)/books:/app/books:ro bookbot:latest books/frankenstein.txt

docker-compose:
	docker-compose run --rm bookbot books/frankenstein.txt

# Podman (same as Docker but uses podman)
podman:
	podman build -t bookbot:latest .

podman-run:
	podman run --rm -v $$(pwd)/books:/app/books:ro bookbot:latest books/frankenstein.txt

# Cleaning
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Demo
demo:
	python main.py books/frankenstein.txt

demo-html:
	python main.py books/frankenstein.txt -f html -o output/report.html
	@echo "Report saved to output/report.html"

demo-viz:
	python main.py books/frankenstein.txt --visualize -o output/
	@echo "Visualizations saved to output/visualizations/"
