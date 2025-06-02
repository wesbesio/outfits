# File: models/database.py
# Revision: 1.0 - Database configuration

from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# Database file path
DB_PATH = Path("outfit_manager.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production
)

def init_db():
    """Initialize database and create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
