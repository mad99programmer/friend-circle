from .database import Base
from sqlalchemy import BigInteger, Column, String, DateTime
from sqlalchemy.sql import func


class User(Base):
    __tablename__="users"
    id = Column(BigInteger, primary_key=True)
    handle = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())