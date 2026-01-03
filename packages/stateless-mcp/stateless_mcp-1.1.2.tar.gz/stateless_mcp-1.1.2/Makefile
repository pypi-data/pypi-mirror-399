.PHONY: help install test lint format clean run docker-build docker-run

help:
	@echo "Stateless MCP - Makefile Commands"
	@echo ""
	@echo "  install       Install dependencies"
	@echo "  test          Run tests"
	@echo "  lint          Run linters"
	@echo "  format        Format code"
	@echo "  clean         Clean build artifacts"
	@echo "  run           Run development server"
	@echo "  run-prod      Run production server with multiple workers"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run Docker container"
	@echo ""

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=stateless_mcp --cov-report=html --cov-report=term

lint:
	ruff check stateless_mcp/
	mypy stateless_mcp/

format:
	black stateless_mcp/ tests/
	ruff check --fix stateless_mcp/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete

run:
	uvicorn stateless_mcp.app:app --reload --host 0.0.0.0 --port 8000

run-prod:
	uvicorn stateless_mcp.app:app --workers 4 --host 0.0.0.0 --port 8000

docker-build:
	docker build -t stateless-mcp:latest .

docker-run:
	docker run -p 8000:8000 stateless-mcp:latest

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down
