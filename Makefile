PROJECT_NAME := FocusUp

DOCKER_COMPOSE := docker-compose.yml

WEB_SERVICE := web
DB_SERVICE := db

ENV_FILE := .env.prod

.PHONY: help build up down logs migrate createsuperuser shell test

help:
	@echo "Использование:"
	@echo "  make build            - Собрать Docker образы"
	@echo "  make up               - Запустить все контейнеры"
	@echo "  make down             - Остановить все контейнеры"
	@echo "  make logs             - Показать логи всех контейнеров"
	@echo "  make migrate          - Выполнить миграции базы данных"
	@echo "  make createsuperuser  - Создать суперпользователя"
	@echo "  make test             - Запустить тесты"

build:
	docker-compose -f $(DOCKER_COMPOSE) build

up:
	docker-compose -f $(DOCKER_COMPOSE) up -d

down:
	docker-compose -f $(DOCKER_COMPOSE) down

logs:
	docker-compose -f $(DOCKER_COMPOSE) logs -f


