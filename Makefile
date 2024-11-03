DOCKER_COMPOSE=docker-compose
PROJECT_NAME=betting-system

.PHONY: help
help:
	@echo "Makefile для управления проектом $(PROJECT_NAME)"
	@echo ""
	@echo "Доступные команды:"
	@echo "  make up                 Запустить все контейнеры через docker-compose"
	@echo "  make down               Остановить и удалить контейнеры"
	@echo "  make build              Собрать Docker образы"
	@echo "  make test               Запустить тесты в контейнерах"
	@echo "  make migrate            Провести миграции базы данных"
	@echo "  make migrate-upgrade    Провести alembic upgrade head"
	@echo "  make migrate-downgrade  Провести alembic downgrade base"
	@echo "  make logs               Посмотреть логи контейнеров"
	@echo "  make clean              Удалить ненужные контейнеры и данные"

# Команды докера
up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

build:
	$(DOCKER_COMPOSE) build

logs:
	$(DOCKER_COMPOSE) logs -f

# Команды миграций
migrate:
	docker exec -it $(PROJECT_NAME)-bet-maker-1 alembic revision --autogenerate -m "new migration"

migrate-upgrade:
	docker exec -it $(PROJECT_NAME)-bet-maker-1 alembic upgrade head

migrate-downgrade:
	docker exec -it $(PROJECT_NAME)-bet-maker-1 alembic downgrade base

# Команды тестов
test:
	$(DOCKER_COMPOSE) run bet-maker pytest -v --disable-warnings
	$(DOCKER_COMPOSE) run line-provider pytest -v --disable-warnings
