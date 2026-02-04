from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import SessionLocal
from app import models
from pydantic import BaseModel
from typing import Optional
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

    parent_comment_id: Optional[int] = None


class CommentAuthorOut(BaseModel):
    id: int
    handle: str


class CommentOut(BaseModel):
    id: int
    content: str
    parent_comment_id: Optional[int]
    created_at: datetime
    author: CommentAuthorOut

from fastapi import HTTPException


@router.post("/", status_code=201)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    # If replying, validate parent comment
    parent_comment = None

    if comment.parent_comment_id is not None:
        parent_comment = (
            db.query(models.Comment)
            .filter(models.Comment.id == comment.parent_comment_id)
            .first()
        )

        if not parent_comment:
            raise HTTPException(
                status_code=404,
                detail="Parent comment not found",
            )
        # just an additional check to know whether parent comment belong to current vent
        if parent_comment.vent_id != comment.vent_id:
            raise HTTPException(
                status_code=400,
                detail="Parent comment belongs to a different vent",
            )

    # Create comment
    new_comment = models.Comment(
        vent_id=comment.vent_id,
        user_id=comment.user_id,
        content=comment.content,
        parent_comment_id=comment.parent_comment_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment





@router.get("/", response_model=list[CommentOut])
def list_comments(
    vent_id: int,
    limit: int = Query(50, ge=1, le=100),
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
            "parent_comment_id": comment.parent_comment_id,
            "created_at": comment.created_at,
            "author": {
                "id": user.id,
                "handle": user.handle,
            },
        }
        for comment, user in results
    ]
