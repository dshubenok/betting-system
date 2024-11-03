import time
from fastapi import FastAPI, Path, HTTPException
import schemas

# Хранение событий в памяти
events: dict[str, schemas.Event] = {
    '1': schemas.Event(event_id='1', coefficient=1.2, deadline=int(time.time()) + 600, state=schemas.EventState.NEW),
    '2': schemas.Event(event_id='2', coefficient=1.15, deadline=int(time.time()) + 60, state=schemas.EventState.NEW),
    '3': schemas.Event(event_id='3', coefficient=1.67, deadline=int(time.time()) + 90, state=schemas.EventState.NEW)
}

app = FastAPI()


# Создание или обновление события
@app.put('/event')
async def create_or_update_event(event: schemas.Event):
    if event.event_id not in events:
        events[event.event_id] = event
        return {"message": "Event created successfully"}

    for field_name, field_value in event.dict(exclude_unset=True).items():
        setattr(events[event.event_id], field_name, field_value)

    return {"message": "Event updated successfully"}


# Получение события по ID
@app.get('/event/{event_id}')
async def get_event(event_id: str = Path(...)):
    if event_id in events:
        return events[event_id]

    raise HTTPException(status_code=404, detail="Event not found")


# Получение всех активных событий
@app.get('/events')
async def get_active_events():
    current_time = int(time.time())
    active_events = [e for e in events.values() if e.state == schemas.EventState.NEW and e.deadline > current_time]
    return active_events


# Обновление статуса события
@app.patch('/event/{event_id}/state')
async def update_event_state(event_id: str, state: schemas.EventState):
    if event_id in events:
        event = events[event_id]
        event.state = state
        return {"message": "Event state updated"}

    raise HTTPException(status_code=404, detail="Event not found")
