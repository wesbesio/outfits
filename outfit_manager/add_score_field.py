# File: add_score_field.py
# Revision: 1.0 - Add score field to outfit table

import os
import sqlite3
import shutil
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

def add_score_field_to_outfits():
    """Add score field to outfit table with data preservation."""
    db_file = "outfit_manager.db"
    backup_file = "outfit_manager_backup_before_score.db"
    
    print("🎯 ADDING SCORE FIELD TO OUTFITS")
    print("=" * 50)
    
    if not os.path.exists(db_file):
        print("❌ Database file not found. Please run the application first.")
        return
    
    # Step 1: Create backup
    if os.path.exists(backup_file):
        os.remove(backup_file)
    shutil.copy2(db_file, backup_file)
    print(f"✅ Created backup at {backup_file}")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Step 2: Check if score field already exists
        cursor.execute("PRAGMA table_info(outfit)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"📋 Current outfit table columns: {column_names}")
        
        if 'score' in column_names:
            print("✅ Score field already exists in outfit table - nothing to do!")
            return
        
        print("🔧 Adding score field to outfit table...")
        
        # Step 3: Read existing outfit data
        cursor.execute("SELECT * FROM outfit")
        existing_outfits = cursor.fetchall()
        print(f"📊 Found {len(existing_outfits)} existing outfits to migrate")
        
        # Get column names for data mapping
        old_column_names = [description[0] for description in cursor.description]
        print(f"📋 Old columns: {old_column_names}")
        
        # Step 4: Create new outfit table with score field
        cursor.execute("""
            CREATE TABLE outfit_new (
                outid INTEGER PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description VARCHAR(1000),
                notes VARCHAR(1000),
                totalcost INTEGER NOT NULL DEFAULT 0,
                score INTEGER NOT NULL DEFAULT 0,
                image BLOB,
                active BOOLEAN NOT NULL DEFAULT 1,
                flag BOOLEAN NOT NULL DEFAULT 0
            )
        """)
        print("✅ Created new outfit table structure with score field")
        
        # Step 5: Migrate data from old table to new table
        if existing_outfits:
            # Build INSERT statement dynamically based on old columns
            insert_columns = []
            select_positions = []
            
            for i, old_col in enumerate(old_column_names):
                if old_col != 'vendorid':  # Skip vendorid if it exists
                    insert_columns.append(old_col)
                    select_positions.append(i)
            
            # Add score with default value
            insert_columns.append('score')
            
            placeholders = ['?' for _ in insert_columns]
            
            insert_sql = f"""
                INSERT INTO outfit_new ({', '.join(insert_columns)})
                VALUES ({', '.join(placeholders)})
            """
            
            for outfit_row in existing_outfits:
                # Extract values for non-vendorid columns
                values = [outfit_row[i] for i in select_positions]
                values.append(0)  # Default score value
                
                cursor.execute(insert_sql, values)
            
            print(f"✅ Migrated {len(existing_outfits)} outfits with default score=0")
        
        # Step 6: Drop old table and rename new table
        cursor.execute("DROP TABLE outfit")
        print("✅ Dropped old outfit table")
        
        cursor.execute("ALTER TABLE outfit_new RENAME TO outfit")
        print("✅ Renamed new table to outfit")
        
        # Step 7: Recreate indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_outid ON outfit (outid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_active ON outfit (active)")
        print("✅ Recreated indexes")
        
        # Step 8: Commit changes
        conn.commit()
        print("✅ Successfully added score field to outfit table")
        
        # Step 9: Verify final structure
        cursor.execute("PRAGMA table_info(outfit)")
        final_columns = cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        print(f"📋 Final outfit table columns: {final_column_names}")
        
        if 'score' in final_column_names:
            print("🎉 SUCCESS: Score field successfully added!")
            
            # Show some sample data
            cursor.execute("SELECT outid, name, score FROM outfit LIMIT 3")
            samples = cursor.fetchall()
            print(f"📊 Sample outfit data:")
            for sample in samples:
                print(f"   ID {sample[0]}: {sample[1]} (score: {sample[2]})")
        else:
            print("❌ FAILED: Score field still missing")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
        
        # Restore backup if something went wrong
        conn.close()
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, db_file)
            print(f"🔄 Restored database from backup")
        raise
        
    finally:
        conn.close()

def verify_score_field():
    """Verify that score field was successfully added."""
    db_file = "outfit_manager.db"
    
    if not os.path.exists(db_file):
        return
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(outfit)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"\n🔍 VERIFICATION:")
        print(f"   Outfit table columns: {column_names}")
        
        if 'score' in column_names:
            print(f"   ✅ SUCCESS: Score field found in outfit table")
            
            # Test querying score
            cursor.execute("SELECT COUNT(*) FROM outfit WHERE score >= 0")
            count = cursor.fetchone()[0]
            print(f"   📊 {count} outfits with valid score values")
        else:
            print(f"   ❌ FAILED: Score field missing from outfit table")
            
    finally:
        conn.close()

if __name__ == "__main__":
    add_score_field_to_outfits()
    verify_score_field()