.PHONY: help build up down logs shell migrate test clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make shell    - Open shell in app container"
	@echo "  make migrate  - Run database migrations"
	@echo "  make test     - Run tests"
	@echo "  make clean    - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec app /bin/bash

migrate:
	docker-compose exec app alembic upgrade head

migrate-create:
	docker-compose exec app alembic revision --autogenerate -m "$(message)"

test:
	docker-compose exec app pytest tests/ -v --cov=app --cov-report=term-missing

clean:
	docker-compose down -v
	docker system prune -f

backup-db:
	docker-compose exec postgres pg_dump -U postgres school_db > backup_$$(date +%Y%m%d_%H%M%S).sql

restore-db:
	docker-compose exec -T postgres psql -U postgres school_db < $(file)

ssl-cert:
	docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot -d yourdomain.uz