from fastapi import Header, HTTPException
from services.db import SessionLocal, User


def get_api_key(x_api_key: str = Header(...)):
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user


def deduct_credit(user: User):
    db = SessionLocal()
    db_user = db.query(User).filter(User.id == user.id).first()

    if db_user.credits <= 0:
        raise HTTPException(status_code=402, detail="No credits left")

    db_user.credits -= 1
    db.commit()
    db.refresh(db_user)
