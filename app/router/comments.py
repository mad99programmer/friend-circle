from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal
from app import models
from pydantic import BaseModel
router = APIRouter(prefix="/comments", tags=["Comments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CommentCreate(BaseModel):
    vent_id: int
    user_id: int
    content: str


class CommentAuthorOut(BaseModel):
    id: int
    handle: str


class CommentOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    author: CommentAuthorOut


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    new_comment = models.Comment(
        vent_id=comment.vent_id,
        user_id=comment.user_id,
        content=comment.content,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment






@router.get("/", response_model=list[CommentOut])
def list_comments(
    vent_id: int,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    results = (
        db.query(models.Comment, models.User)
        .join(models.User, models.Comment.user_id == models.User.id)
        .filter(
            models.Comment.vent_id == vent_id,
            models.Comment.is_hidden == False,
        )
        .order_by(models.Comment.created_at.asc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return [
        {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at,
            "author": {
                "id": user.id,
                "handle": user.handle,
            },
        }
        for comment, user in results
    ]
