import pytest
from httpx import AsyncClient, Response, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, MagicMock

from app.app import app
from app.db import Base, get_db

# Настраиваем SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def override_get_db():
    def _get_test_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = _get_test_db
    yield
    if previous_override:
        app.dependency_overrides[get_db] = previous_override
    else:
        del app.dependency_overrides[get_db]

@pytest.mark.asyncio
async def test_place_bet(override_get_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        # Мок для запроса события
        mock_event = {
            "event_id": "1",
            "coefficient": 1.2,
            "deadline": 9999999999,
            "state": 1
        }

        mock_event_response = Response(
            status_code=200,
            json=mock_event,
            request=MagicMock()
        )
        mock_event_response.raise_for_status = MagicMock()

        # Мок для списка ставок
        mock_bets_response = Response(
            status_code=200,
            json=[{
                "id": 1,
                "event_id": "1",
                "amount": 100.50,
                "status": "PENDING"
            }],
            request=MagicMock()
        )
        mock_bets_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get") as mock_get:
            def mock_get_side_effect(url, **kwargs):
                if "event/" in url:
                    return mock_event_response
                elif "events" in url:
                    return Response(200, json=[mock_event], request=MagicMock())
                else:
                    return mock_bets_response

            mock_get.side_effect = mock_get_side_effect

            bet_data = {
                "event_id": "1",
                "amount": 100.50
            }

            response = await ac.post("/bet", json=bet_data)
            if response.status_code != 200:
                print("Error response:", response.json())
            assert response.status_code == 200

            bet = response.json()
            assert isinstance(bet, dict)
            assert bet["event_id"] == "1"
            assert bet["amount"] == 100.50
            assert "status" in bet
            assert "id" in bet

            response = await ac.get("/bets")
            assert response.status_code == 200
            bets = response.json()
            assert isinstance(bets, list)
            assert len(bets) == 1
            assert bets[0]["event_id"] == "1"
            assert bets[0]["amount"] == 100.50
            assert "status" in bets[0]
            assert "id" in bets[0]

@pytest.mark.asyncio
async def test_place_bet_on_finished_event(override_get_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        mock_event = {
            "event_id": "1",
            "coefficient": 1.2,
            "deadline": 9999999999,
            "state": 2
        }

        mock_response = Response(
            status_code=200,
            json=mock_event,
            request=MagicMock()
        )
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response

            bet_data = {
                "event_id": "1",
                "amount": 100.50
            }

            response = await ac.post("/bet", json=bet_data)
            assert response.status_code == 400
            assert "Cannot place bet on a finished event" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_events(override_get_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        mock_events = [{
            "event_id": "1",
            "coefficient": 1.2,
            "deadline": 9999999999,
            "state": 1
        }]

        mock_response = Response(
            status_code=200,
            json=mock_events,
            request=MagicMock()
        )
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = mock_response
            response = await ac.get("/events")
            assert response.status_code == 200
            events = response.json()
            assert isinstance(events, list)
            assert len(events) == 1
            assert events[0]["event_id"] == "1"
