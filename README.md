## Betting System

Betting System — это система для ставок на события. Она состоит из двух микросервисов:
- **line-provider** — сервис, который предоставляет информацию о событиях для ставок.
- **bet-maker** — сервис, который принимает ставки на события от пользователей.

Система работает в асинхронном режиме и включает взаимодействие между сервисами через HTTP-запросы. Данные о ставках хранятся в базе данных Postgres, а события генерируются и управляются сервисом `line-provider`.

## Структура API

### Сервис line-provider

- `GET /events`: Возвращает список событий, доступных для ставок.
- `GET /event/{event_id}`: Возвращает информацию о конкретном событии.
- `PUT /event`: Создаёт новое событие.
- `PATCH /event/{event_id}/state`: Обновляет статус события (например, завершение события).

### Сервис bet-maker

- `GET /events`: Возвращает список событий, на которые можно сделать ставку (интеграция с `line-provider`).
- `POST /bet`: Принимает ставку на событие.
- `GET /bets`: Возвращает список всех ставок.

## Установка и запуск

### Клонирование репозитория

```bash
git clone https://github.com/dshubenok/betting-system.git
cd betting-system
```

### Настройка окружения
Перед первым запуском переименуйте файл example.env в .env:

```bash
mv example.env .env
```

### Запуск через Docker
1. Соберите и запустите все сервисы: `make up`
2. (опционально) Посмотрите логи: `make logs`
3. (опционально) Остановите сервисы, когда работа завершена: `make down`

### Запуск тестов
Команда `make test`, тесты запустятся в контейнере
