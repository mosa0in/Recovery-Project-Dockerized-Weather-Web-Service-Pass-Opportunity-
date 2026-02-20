.PHONY: help build up down logs test clean stop start

help:
	@echo "Weather API Service - Make Commands"
	@echo "===================================="
	@echo "make build          - Build Docker image"
	@echo "make up             - Start service with docker-compose"
	@echo "make down           - Stop and remove containers"
	@echo "make logs           - View service logs"
	@echo "make test           - Run API tests"
	@echo "make start          - Start service in background"
	@echo "make stop           - Stop running service"
	@echo "make clean          - Remove containers and images"
	@echo "make setup          - Setup environment and build"
	@echo "make dev            - Run in development mode"

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env and add your OPENWEATHER_API_KEY"; \
	fi
	@make build

build:
	docker-compose build

up:
	docker-compose up

start:
	docker-compose up -d

down:
	docker-compose down

stop:
	docker-compose stop

logs:
	docker-compose logs -f weather-api

test:
	@chmod +x test_api.sh
	./test_api.sh

dev:
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up

clean:
	docker-compose down -v
	docker image rm weather-api:latest || true

clean-all: clean
	docker system prune -f

restart: down start logs

health:
	@curl -s http://localhost:5000/health | python -m json.tool || echo "Service unavailable"

weather-london:
	@curl -s "http://localhost:5000/weather?city=London" | python -m json.tool

weather-paris:
	@curl -s "http://localhost:5000/weather?city=Paris" | python -m json.tool
