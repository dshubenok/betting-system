import decimal
import enum
from pydantic import BaseModel, ConfigDict
from typing import Optional

class BetCreate(BaseModel):
    event_id: str
    amount: float

class BetResponse(BetCreate):
    id: int
    status: str

    model_config = ConfigDict(from_attributes=True)

# Определяем состояние события
class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3

class Event(BaseModel):
    event_id: str
    coefficient: Optional[decimal.Decimal] = None
    deadline: Optional[int] = None  # timestamp
    state: Optional[EventState] = None

    model_config = ConfigDict(from_attributes=True)
