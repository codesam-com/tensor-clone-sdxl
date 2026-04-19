from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from services.db import SessionLocal, User

router = APIRouter()

class CreateUserRequest(BaseModel):
    
    pass

@router.post("/register")
def register():
    db = SessionLocal()

    api_key = str(uuid.uuid4())

    user = User(api_key=api_key, credits=100)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"api_key": api_key, "credits": user.credits}

@router.get("/me")
def me(x_api_key: str):
    db = SessionLocal()
    user = db.query(User).filter(User.api_key == x_api_key).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid key")

    return {"credits": user.credits}
