# File: models/database.py
# Revision: 4.0 - Database configuration

from sqlmodel import create_engine, Session, SQLModel
from . import Vendor, Piece, Component, Outfit, Out2Comp # Import models to ensure they are registered with SQLModel

DATABASE_FILE = "outfit_manager.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

engine = create_engine(DATABASE_URL, echo=True) # echo=True for SQL logging

def create_db_and_tables():
    """Creates all SQLModel tables in the database."""
    SQLModel.metadata.create_all(engine)
    print(f"Database and tables created at {DATABASE_FILE}")

def get_session():
    """Dependency to yield a database session."""
    with Session(engine) as session:
        yield session