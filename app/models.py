from .database import Base
from sqlalchemy import BigInteger, Column, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.sql import func


class User(Base):
    __tablename__="users"
    id = Column(BigInteger, primary_key=True)
    handle = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vent(Base):
    __tablename__="vents"
    id = Column(BigInteger,primary_key=True)
    content = Column(String,nullable=True)
    user_id = Column(BigInteger,ForeignKey('users.id',ondelete="CASCADE"),nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class Comment(Base):
    __tablename__ = "comments"

    id = Column(BigInteger, primary_key=True)
    vent_id = Column(
        BigInteger,
        ForeignKey("vents.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
