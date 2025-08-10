from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import Generator
import os
from dotenv import load_dotenv

# Database setup
try:
    load_dotenv('.env.prod')
except:
    pass  # Environment variables may be set directly
    
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")
    
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()