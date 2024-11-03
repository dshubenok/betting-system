from sqlalchemy import Column, String, Float, Integer, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class BetStatus(enum.Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"

class Bet(Base):
    __tablename__ = "bets"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, index=True)
    amount = Column(Float)
    status = Column(Enum(BetStatus), default=BetStatus.PENDING)
