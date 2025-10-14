.PHONY: help install dev test clean docker-up docker-down docker-build migrate init-db

help:
	@echo "Market Intelligence Platform - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install backend dependencies"
	@echo "  make dev          - Start development server"
	@echo "  make test         - Run tests with coverage"
	@echo "  make clean        - Clean cache and temporary files"
	@echo "  make docker-up    - Start all Docker services"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-build - Build Docker images"
	@echo "  make migrate      - Run database migrations"
	@echo "  make init-db      - Initialize database with test users"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with flake8"

install:
	cd backend && pip install -r requirements.txt

dev:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf backend/htmlcov
	rm -rf backend/.coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f

migrate:
	cd backend && alembic upgrade head

migrate-create:
	cd backend && alembic revision --autogenerate -m "$(msg)"

migrate-down:
	cd backend && alembic downgrade -1

init-db:
	cd backend && python scripts/init_db.py

format:
	cd backend && black app/ tests/

lint:
	cd backend && flake8 app/ tests/

db-shell:
	docker-compose exec postgres psql -U marketintel -d market_intelligence

backend-shell:
	docker-compose exec backend bash
