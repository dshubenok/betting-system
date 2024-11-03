from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
import crud
import db
import schemas

app = FastAPI()


# Получение списка событий из line-provider
@app.get("/events", response_model=list[schemas.Event])
async def get_events():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://line-provider:8080/events", timeout=5.0)
            response.raise_for_status()  # Проверка статуса ответа
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")
    return response.json()


# Совершение ставки
@app.post("/bet", response_model=schemas.BetResponse)
async def place_bet(bet: schemas.BetCreate, db: Session = Depends(db.get_db)):
    # Проверяем, существует ли событие
    async with httpx.AsyncClient() as client:
        try:
            event_response = await client.get(f"http://line-provider:8080/event/{bet.event_id}", timeout=5.0)
            event_response.raise_for_status()  # Проверка статуса ответа
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch event: {str(e)}")

    event_data = event_response.json()

    # Используем перечисление для проверки статуса события
    if event_data["state"] != 1:
        raise HTTPException(status_code=400, detail="Cannot place bet on a finished event")

    # Создаём ставку
    new_bet = crud.create_bet(db=db, bet=bet)
    return new_bet


# Получение всех ставок
@app.get("/bets", response_model=list[schemas.BetResponse])
async def get_bets(db: Session = Depends(db.get_db)):
    return crud.get_bets(db)
