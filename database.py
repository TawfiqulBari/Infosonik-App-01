import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_recycle=300,    # Recycle connections after 5 minutes
    pool_size=10,        # Maximum number of connections in the pool
    max_overflow=20,     # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,     # Timeout for getting a connection from the pool
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c statement_timeout=30000"  # Query timeout (30 seconds)
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization will be handled in startup event
def wait_for_database():
    """Wait for database to be available with retry logic"""
    max_retries = 30
    retry_interval = 2

    for attempt in range(max_retries):
        try:
            # Test database connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print(f"Database connection established after {attempt + 1} attempts")
            return True
        except Exception as e:
            print(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                print("Max retries exceeded. Database connection failed.")
                raise e
    return False

def create_tables():
    """Create all database tables"""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")