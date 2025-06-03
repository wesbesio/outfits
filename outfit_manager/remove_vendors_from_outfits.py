# File: remove_vendor_from_outfits.py
# Revision: 1.0 - Remove vendorid column from outfit table

import sqlite3
import os
from pathlib import Path

def remove_vendor_from_outfits():
    """Remove vendorid column from outfit table."""
    db_path = Path("outfit_manager.db")
    
    if not db_path.exists():
        print("❌ Database file not found. Please run the application first.")
        return
    
    print("🔄 REMOVING VENDOR FROM OUTFITS")
    print("=" * 50)
    
    # Backup database first
    backup_path = Path("outfit_manager_backup.db")
    if backup_path.exists():
        backup_path.unlink()
    
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Created backup at {backup_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current outfit table structure
        cursor.execute("PRAGMA table_info(outfit)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Current outfit table columns: {column_names}")
        
        if 'vendorid' not in column_names:
            print("✅ vendorid column not found in outfit table - nothing to remove")
            return
        
        print("🔧 Removing vendorid column from outfit table...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to:
        # 1. Create new table without vendorid
        # 2. Copy data from old table to new table
        # 3. Drop old table
        # 4. Rename new table
        
        # Step 1: Create new outfit table without vendorid
        cursor.execute("""
            CREATE TABLE outfit_new (
                outid INTEGER PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description VARCHAR(1000),
                notes VARCHAR(1000),
                totalcost INTEGER NOT NULL DEFAULT 0,
                image BLOB,
                active BOOLEAN NOT NULL DEFAULT 1,
                flag BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        print("✅ Created new outfit table structure")
        
        # Step 2: Copy data from old table to new table (excluding vendorid)
        cursor.execute("""
            INSERT INTO outfit_new (outid, name, description, notes, totalcost, image, active, flag)
            SELECT outid, name, description, notes, totalcost, image, active, flag
            FROM outfit
        """)
        
        row_count = cursor.rowcount
        print(f"✅ Copied {row_count} rows to new table")
        
        # Step 3: Drop old table
        cursor.execute("DROP TABLE outfit")
        print("✅ Dropped old outfit table")
        
        # Step 4: Rename new table
        cursor.execute("ALTER TABLE outfit_new RENAME TO outfit")
        print("✅ Renamed new table to outfit")
        
        # Recreate any indexes that might have existed
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_outid ON outfit (outid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_active ON outfit (active)")
        
        # Commit changes
        conn.commit()
        print("✅ Successfully removed vendorid from outfit table")
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(outfit)")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        print(f"📋 Final outfit table columns: {final_column_names}")
        
        if 'vendorid' not in final_column_names:
            print("🎉 SUCCESS: vendorid column successfully removed!")
        else:
            print("❌ FAILED: vendorid column still present")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        
        # Restore backup if something went wrong
        conn.close()
        if backup_path.exists():
            shutil.copy2(backup_path, db_path)
            print(f"🔄 Restored database from backup")
        raise
        
    finally:
        conn.close()

def verify_removal():
    """Verify that vendorid was successfully removed."""
    db_path = Path("outfit_manager.db")
    
    if not db_path.exists():
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(outfit)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\n🔍 VERIFICATION:")
        print(f"   Outfit table columns: {column_names}")
        
        if 'vendorid' not in column_names:
            print(f"   ✅ SUCCESS: vendorid successfully removed from outfit table")
        else:
            print(f"   ❌ FAILED: vendorid still present in outfit table")
            
    finally:
        conn.close()

if __name__ == "__main__":
    remove_vendor_from_outfits()
    verify_removal()