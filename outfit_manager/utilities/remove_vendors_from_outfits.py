# File: utilities/remove_vendors_from_outfits.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import sqlite3
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

def remove_vendor_from_outfits():
    """Remove vendorid column from outfit table."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_path = Path("outfit_manager.db")
        
        print("🔄 REMOVING VENDOR FROM OUTFITS")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")
        
        if not db_path.exists():
            print("❌ Database file not found. Please run the application first.")
            return
        
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
            # Check if score column should be included
            if 'score' in column_names:
                print("   📊 Score column detected - including in new table")
                create_table_sql = """
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
                """
                select_columns = "outid, name, description, notes, totalcost, score, image, active, flag"
            else:
                print("   📊 Score column not detected - creating table without score")
                create_table_sql = """
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
                """
                select_columns = "outid, name, description, notes, totalcost, image, active, flag"
            
            cursor.execute(create_table_sql)
            print("✅ Created new outfit table structure")
            
            # Step 2: Copy data from old table to new table (excluding vendorid)
            copy_sql = f"""
                INSERT INTO outfit_new ({select_columns})
                SELECT {select_columns}
                FROM outfit
            """
            cursor.execute(copy_sql)
            
            row_count = cursor.rowcount
            print(f"✅ Copied {row_count} rows to new table")
            
            # Step 3: Drop old table
            cursor.execute("DROP TABLE outfit")
            print("✅ Dropped old outfit table")
            
            # Step 4: Rename new table
            cursor.execute("ALTER TABLE outfit_new RENAME TO outfit")
            print("✅ Renamed new table to outfit")
            
            # Step 5: Recreate any indexes that might have existed
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_outid ON outfit (outid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_outfit_active ON outfit (active)")
            print("✅ Recreated indexes")
            
            # Step 6: Recreate foreign key constraints if needed
            # Check if there are any tables that reference outfit.outid
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND sql LIKE '%REFERENCES outfit%'
            """)
            referencing_tables = cursor.fetchall()
            
            if referencing_tables:
                print(f"📋 Found tables referencing outfit: {[t[0] for t in referencing_tables]}")
                # Foreign keys should still work since we kept the same outid primary key
                print("✅ Foreign key relationships should remain intact")
            
            # Step 7: Commit changes
            conn.commit()
            print("✅ Successfully removed vendorid from outfit table")
            
            # Step 8: Verify final structure
            cursor.execute("PRAGMA table_info(outfit)")
            final_columns = cursor.fetchall()
            final_column_names = [col[1] for col in final_columns]
            
            print(f"📋 Final outfit table columns: {final_column_names}")
            
            if 'vendorid' not in final_column_names:
                print("🎉 SUCCESS: vendorid column successfully removed!")
            else:
                print("❌ FAILED: vendorid column still present")
            
            # Show sample data to verify integrity
            cursor.execute("SELECT outid, name, totalcost FROM outfit LIMIT 3")
            samples = cursor.fetchall()
            if samples:
                print(f"📊 Sample outfit data after migration:")
                for sample in samples:
                    print(f"   ID {sample[0]}: {sample[1]} (cost: ${sample[2]/100:.2f})")
                
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
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def verify_removal():
    """Verify that vendorid was successfully removed."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_path = Path("outfit_manager.db")
        
        if not db_path.exists():
            print("❌ Database file not found for verification")
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
                
                # Check data integrity
                cursor.execute("SELECT COUNT(*) FROM outfit")
                outfit_count = cursor.fetchone()[0]
                print(f"   📊 {outfit_count} outfits remain in table")
                
                # Check if score field is present
                if 'score' in column_names:
                    print(f"   ✅ Score field preserved during migration")
                    cursor.execute("SELECT AVG(score) FROM outfit WHERE score > 0")
                    avg_score = cursor.fetchone()[0]
                    if avg_score:
                        print(f"      Average score: {avg_score:.1f}")
                else:
                    print(f"   📊 Score field not present (expected if not added yet)")
                
                # Check foreign key integrity
                cursor.execute("""
                    SELECT COUNT(*) FROM out2comp o2c 
                    LEFT JOIN outfit o ON o2c.outid = o.outid 
                    WHERE o.outid IS NULL
                """)
                orphaned_refs = cursor.fetchone()[0]
                
                if orphaned_refs == 0:
                    print(f"   ✅ All outfit references in out2comp table are valid")
                else:
                    print(f"   ⚠️  {orphaned_refs} orphaned references found in out2comp")
                    
            else:
                print(f"   ❌ FAILED: vendorid still present in outfit table")
                
        except sqlite3.OperationalError as e:
            print(f"   ❌ Database error during verification: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def check_vendor_references():
    """Check for any remaining vendor references in the database."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_path = Path("outfit_manager.db")
        
        if not db_path.exists():
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            print(f"\n🔍 CHECKING VENDOR REFERENCES:")
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            vendor_refs_found = False
            
            for table in tables:
                table_name = table[0]
                
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Check for vendor-related columns
                vendor_columns = [col[1] for col in columns if 'vendor' in col[1].lower()]
                
                if vendor_columns:
                    print(f"   📋 {table_name}: {vendor_columns}")
                    vendor_refs_found = True
                    
                    # Check if these are valid references
                    for col in vendor_columns:
                        if col == 'vendorid' and table_name == 'component':
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col} IS NOT NULL")
                            count = cursor.fetchone()[0]
                            print(f"      ✅ {count} components with vendor references (expected)")
                        elif col == 'vendorid' and table_name == 'outfit':
                            print(f"      ❌ Unexpected vendorid in outfit table!")
            
            if not vendor_refs_found:
                print(f"   ℹ️  No vendor reference columns found (except in component table)")
            
            # Check vendor table integrity
            cursor.execute("SELECT COUNT(*) FROM vendor WHERE active = 1")
            active_vendors = cursor.fetchone()[0]
            print(f"   📊 {active_vendors} active vendors in vendor table")
            
        except Exception as e:
            print(f"   ❌ Error checking vendor references: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    remove_vendor_from_outfits()
    verify_removal()
    check_vendor_references()