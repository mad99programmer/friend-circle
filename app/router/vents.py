from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from pydantic import BaseModel
from datetime import datetime
router = APIRouter(prefix="/vents", tags=["Vents"])



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class AuthorOut(BaseModel):
    id: int
    handle: str


class VentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: AuthorOut
    
class VentCreate(BaseModel):
    user_id: int
    content: str

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vent(vent: VentCreate, db: Session = Depends(get_db)):
    new_vent = models.Vent(
        user_id=vent.user_id,
        content=vent.content
    )

    db.add(new_vent)
    db.commit()
    db.refresh(new_vent)

    return new_vent



@router.get("/", response_model=list[VentOut])
def list_vents(limit: int = Query(20, ge=1, le=50),
               offset: int = Query(0, ge=0),db: Session = Depends(get_db)):
    results = (
        db.query(models.Vent, models.User)
        .join(models.User, models.Vent.user_id == models.User.id)
        .filter(models.Vent.is_hidden == False)
        .order_by(models.Vent.created_at.desc()).limit(limit).offset(offset)
        .all()
    )

    return [
        {
            "id": vent.id,
            "content": vent.content,
            "created_at": vent.created_at,
            "author": {
                "id": user.id,
                "handle": user.handle,
            },
        }
        for vent, user in results
    ]
