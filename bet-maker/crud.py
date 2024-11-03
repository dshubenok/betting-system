from sqlalchemy.orm import Session
import models, schemas

def create_bet(db: Session, bet: schemas.BetCreate) -> models.Bet:
    db_bet = models.Bet(event_id=bet.event_id, amount=bet.amount)
    db.add(db_bet)
    db.commit()
    db.refresh(db_bet)
    return db_bet

def get_bets(db: Session) -> list[models.Bet]:
    return db.query(models.Bet).all()
