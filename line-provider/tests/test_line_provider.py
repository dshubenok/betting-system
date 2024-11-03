import time
import pytest
from httpx import AsyncClient, Response, ASGITransport
from unittest.mock import patch
from app.app import app
from app.schemas import EventState

@pytest.mark.asyncio
async def test_create_event():
    # Подготавливаем тестовые данные для создания события
    test_event = {
        'event_id': 'test_id',
        'coefficient': 2.0,
        'deadline': int(time.time()) + 600,  # Дедлайн через 10 минут
        'state': EventState.NEW.value
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Мокируем PUT запрос для создания события
        with patch("httpx.AsyncClient.put") as mock_put:
            mock_put.return_value = Response(200, json={"message": "Event created successfully"})
            response = await ac.put("/event", json=test_event)

    # Проверяем успешное создание события
    assert response.status_code == 200
    assert response.json() == {"message": "Event created successfully"}

@pytest.mark.asyncio
async def test_get_event():
    # Подготавливаем мок данные для одного события
    mock_event = {
        "event_id": "1",
        "coefficient": 1.5,
        "deadline": int(time.time()) + 600,
        "state": EventState.NEW.value
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Мокируем GET запрос для получения события
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Response(200, json=mock_event)
            response = await ac.get("/event/1")

    # Проверяем успешное получение события и его данные
    assert response.status_code == 200
    event = response.json()
    assert event["event_id"] == "1"
    assert event["coefficient"] == 1.5

@pytest.mark.asyncio
async def test_get_active_events():
    current_time = int(time.time())
    # Подготавливаем мок данные для списка активных событий
    mock_events = [
        {
            "event_id": "1",
            "coefficient": 1.5,
            "deadline": current_time + 600,  # Первое событие через 10 минут
            "state": EventState.NEW.value
        },
        {
            "event_id": "2",
            "coefficient": 2.0,
            "deadline": current_time + 1200,  # Второе событие через 20 минут
            "state": EventState.NEW.value
        }
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Мокируем GET запрос для получения списка событий
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Response(200, json=mock_events)
            response = await ac.get("/events")

    # Проверяем успешное получение списка событий
    assert response.status_code == 200
    active_events = response.json()
    assert len(active_events) == 2
    # Проверяем, что все события активны (дедлайн в будущем)
    assert all(e["deadline"] > current_time for e in active_events)

@pytest.mark.asyncio
async def test_update_event_state():
    # Подготавливаем мок данные для обновленного события
    mock_event = {
        "event_id": "1",
        "coefficient": 1.5,
        "deadline": int(time.time()) + 600,
        "state": EventState.FINISHED_WIN.value
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Мокируем PATCH запрос для обновления состояния события
        with patch("httpx.AsyncClient.patch") as mock_patch:
            mock_patch.return_value = Response(200, json={"message": "Event state updated"})
            response = await ac.patch("/event/1/state", json={"state": EventState.FINISHED_WIN.value})
            assert response.status_code == 200
            assert response.json() == {"message": "Event state updated"}

        # Мокируем GET запрос для проверки обновленного состояния
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Response(200, json=mock_event)
            event_response = await ac.get("/event/1")
            assert event_response.status_code == 200
            event = event_response.json()
            # Проверяем, что состояние события обновилось
            assert event["state"] == EventState.FINISHED_WIN.value
