import decimal
import enum
from pydantic import BaseModel
from typing import Optional

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
