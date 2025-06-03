# File: force_recreate_db.py
# Revision: 1.0 - Force recreation of database with proper schema

import os
from sqlmodel import SQLModel, create_engine, Session

def force_recreate_database():
    """Force recreate the database ensuring pieceid is included."""
    db_file = "outfit_manager.db"
    
    print("🔄 FORCING DATABASE RECREATION")
    print("=" * 50)
    
    # Step 1: Remove existing database
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"✅ Removed existing {db_file}")
    
    # Step 2: Clear SQLModel metadata cache
    SQLModel.metadata.clear()
    print("✅ Cleared SQLModel metadata cache")
    
    # Step 3: Import models fresh
    try:
        from models import Vendor, Piece, Component, Outfit, Out2Comp
        print("✅ Imported all models")
        
        # Check Component model has pieceid before creating
        print(f"\n🔍 Checking Component model:")
        print(f"   Model: {Component}")
        
        if hasattr(Component, '__annotations__'):
            annotations = Component.__annotations__
            print(f"   Annotations: {list(annotations.keys())}")
            if 'pieceid' in annotations:
                print(f"   ✅ pieceid found in annotations")
            else:
                print(f"   ❌ pieceid NOT in annotations")
                return
        
    except Exception as e:
        print(f"❌ Error importing models: {e}")
        return
    
    # Step 4: Create engine and tables
    try:
        engine = create_engine(f"sqlite:///{db_file}", echo=True)
        print(f"✅ Created engine")
        
        # Show what tables will be created
        print(f"\n📋 Tables to be created:")
        for table_name, table in SQLModel.metadata.tables.items():
            columns = [col.name for col in table.columns]
            print(f"   {table_name}: {columns}")
            
            if table_name == 'component':
                if 'pieceid' in columns:
                    print(f"   ✅ pieceid will be created in component table")
                else:
                    print(f"   ❌ pieceid MISSING from component table metadata")
                    return
        
        # Create all tables
        SQLModel.metadata.create_all(engine)
        print(f"✅ Created all tables")
        
        # Step 5: Verify database schema
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print(f"\n🔍 Verifying created schema:")
        cursor.execute("PRAGMA table_info(component)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"   Component table columns: {column_names}")
        
        if 'pieceid' in column_names:
            print(f"   ✅ SUCCESS: pieceid created in database!")
        else:
            print(f"   ❌ FAILED: pieceid still missing from database")
            
        conn.close()
        
        # Step 6: Seed initial data
        print(f"\n🌱 Seeding initial data...")
        from services.seed_data import seed_initial_data
        with Session(engine) as session:
            seed_initial_data(session)
        print(f"✅ Seeded initial data")
        
        print(f"\n🎉 Database recreation complete!")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    force_recreate_database()