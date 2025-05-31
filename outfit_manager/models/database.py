from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database URL - use SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./outfit_manager.db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database and tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Database session dependency"""
    with Session(engine) as session:
        yield session