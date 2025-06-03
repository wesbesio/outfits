# File: check_schema.py
# Revision: 1.0 - Check current database schema

import sqlite3
from pathlib import Path

def check_database_schema():
    """Check the current database schema to diagnose missing columns."""
    db_path = Path("outfit_manager.db")
    
    if not db_path.exists():
        print("❌ Database file 'outfit_manager.db' not found")
        print("   Run your FastAPI application first to create the database")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("📊 CURRENT DATABASE SCHEMA")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table_name in tables:
            table_name = table_name[0]
            print(f"\n🔍 Table: {table_name}")
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   Columns:")
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                pk_indicator = " (PK)" if pk else ""
                null_indicator = " NOT NULL" if notnull else ""
                default_indicator = f" DEFAULT {default}" if default else ""
                print(f"     - {name}: {type_}{pk_indicator}{null_indicator}{default_indicator}")
        
        print("\n" + "=" * 50)
        print("🎯 EXPECTED vs ACTUAL for Component table:")
        
        expected_columns = [
            "comid", "name", "brand", "cost", "description", "notes", 
            "vendorid", "pieceid", "image", "active", "flag"
        ]
        
        cursor.execute("PRAGMA table_info(component)")
        actual_columns = [col[1] for col in cursor.fetchall()]
        
        print(f"   Expected: {expected_columns}")
        print(f"   Actual:   {actual_columns}")
        
        missing = set(expected_columns) - set(actual_columns)
        extra = set(actual_columns) - set(expected_columns)
        
        if missing:
            print(f"   ❌ Missing: {list(missing)}")
        if extra:
            print(f"   ➕ Extra:   {list(extra)}")
        if not missing and not extra:
            print("   ✅ Schema matches expected structure")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_schema()