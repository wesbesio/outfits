# File: test_clean_models.py
# Revision: 1.0 - Test clean model creation with fresh database

import os
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional

# Clean model definitions for testing
class TestVendor(SQLModel, table=True):
    __tablename__ = "test_vendor"
    venid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    active: bool = Field(default=True)

class TestPiece(SQLModel, table=True):
    __tablename__ = "test_piece"
    piecid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    active: bool = Field(default=True)

class TestComponent(SQLModel, table=True):
    __tablename__ = "test_component"
    comid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    brand: Optional[str] = Field(default=None, max_length=100)
    cost: int = Field(default=0)
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    vendorid: Optional[int] = Field(default=None, foreign_key="test_vendor.venid")
    pieceid: Optional[int] = Field(default=None, foreign_key="test_piece.piecid")
    image: Optional[bytes] = Field(default=None)
    active: bool = Field(default=True)
    flag: bool = Field(default=False)

def test_clean_database():
    """Test creating a clean database with explicit models."""
    test_db = "test_clean.db"
    
    # Remove test db if it exists
    if os.path.exists(test_db):
        os.remove(test_db)
        print(f"🗑️  Removed existing {test_db}")
    
    print("🧪 TESTING CLEAN MODEL CREATION")
    print("=" * 50)
    
    try:
        # Create engine
        engine = create_engine(f"sqlite:///{test_db}", echo=True)
        print(f"✅ Created engine for {test_db}")
        
        # Check metadata before creation
        print(f"\n📋 Tables in metadata before creation:")
        for table_name, table in SQLModel.metadata.tables.items():
            if 'test_' in table_name:
                print(f"   {table_name}: {[col.name for col in table.columns]}")
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        print(f"✅ Created all tables")
        
        # Check actual database schema
        import sqlite3
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'test_%'")
        tables = cursor.fetchall()
        
        print(f"\n🔍 Created tables in database:")
        for table_name in tables:
            table_name = table_name[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"   {table_name}: {column_names}")
            
            if table_name == 'test_component':
                if 'pieceid' in column_names:
                    print(f"   ✅ pieceid found in test_component!")
                else:
                    print(f"   ❌ pieceid MISSING from test_component")
        
        conn.close()
        
        # Test inserting data
        with Session(engine) as session:
            vendor = TestVendor(name="Test Vendor")
            piece = TestPiece(name="Test Piece")
            session.add(vendor)
            session.add(piece)
            session.commit()
            session.refresh(vendor)
            session.refresh(piece)
            
            component = TestComponent(
                name="Test Component",
                vendorid=vendor.venid,
                pieceid=piece.piecid,
                cost=1000
            )
            session.add(component)
            session.commit()
            print(f"✅ Successfully created test data with pieceid={component.pieceid}")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"🗑️  Cleaned up {test_db}")

if __name__ == "__main__":
    test_clean_database()