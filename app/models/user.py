from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from .base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    password_hash = Column(String(128))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)