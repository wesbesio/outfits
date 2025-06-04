# File: utilities/force_recreate_db.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel, create_engine, Session

def force_recreate_database():
    """Force recreate the database ensuring pieceid is included."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_file = "outfit_manager.db"
        
        print("🔄 FORCING DATABASE RECREATION")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")
        
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
            
            # Check Outfit model has score and no vendorid
            print(f"\n🔍 Checking Outfit model:")
            print(f"   Model: {Outfit}")
            
            if hasattr(Outfit, '__annotations__'):
                outfit_annotations = Outfit.__annotations__
                print(f"   Annotations: {list(outfit_annotations.keys())}")
                if 'score' in outfit_annotations:
                    print(f"   ✅ score found in annotations")
                else:
                    print(f"   ❌ score NOT in annotations")
                    return
                if 'vendorid' not in outfit_annotations:
                    print(f"   ✅ vendorid correctly removed from annotations")
                else:
                    print(f"   ⚠️  vendorid still present in annotations")
                    return
            
            # Check all other models
            print(f"\n🔍 Checking all model structures:")
            models_to_check = [
                ('Vendor', Vendor),
                ('Piece', Piece),
                ('Out2Comp', Out2Comp)
            ]
            
            for model_name, model_class in models_to_check:
                if hasattr(model_class, '__annotations__'):
                    annotations = model_class.__annotations__
                    print(f"   {model_name}: {list(annotations.keys())}")
            
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
                        
                if table_name == 'outfit':
                    if 'score' in columns:
                        print(f"   ✅ score will be created in outfit table")
                    else:
                        print(f"   ❌ score MISSING from outfit table metadata")
                        return
                    if 'vendorid' not in columns:
                        print(f"   ✅ vendorid correctly excluded from outfit table")
                    else:
                        print(f"   ❌ vendorid still present in outfit table metadata")
                        return
            
            # Create all tables
            SQLModel.metadata.create_all(engine)
            print(f"✅ Created all tables")
            
            # Step 5: Verify database schema
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            print(f"\n🔍 Verifying created schema:")
            
            # Check component table
            cursor.execute("PRAGMA table_info(component)")
            component_columns = cursor.fetchall()
            component_column_names = [col[1] for col in component_columns]
            
            print(f"   Component table columns: {component_column_names}")
            
            if 'pieceid' in component_column_names:
                print(f"   ✅ SUCCESS: pieceid created in component table!")
            else:
                print(f"   ❌ FAILED: pieceid still missing from component table")
                
            # Check outfit table
            cursor.execute("PRAGMA table_info(outfit)")
            outfit_columns = cursor.fetchall()
            outfit_column_names = [col[1] for col in outfit_columns]
            
            print(f"   Outfit table columns: {outfit_column_names}")
            
            if 'score' in outfit_column_names:
                print(f"   ✅ SUCCESS: score created in outfit table!")
            else:
                print(f"   ❌ FAILED: score still missing from outfit table")
                
            if 'vendorid' not in outfit_column_names:
                print(f"   ✅ SUCCESS: vendorid excluded from outfit table!")
            else:
                print(f"   ❌ FAILED: vendorid still present in outfit table")
            
            # Check all other tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = cursor.fetchall()
            print(f"\n📊 All created tables:")
            for table in all_tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_columns = cursor.fetchall()
                table_column_names = [col[1] for col in table_columns]
                print(f"   {table_name}: {len(table_column_names)} columns")
            
            # Check foreign key constraints
            print(f"\n🔗 Foreign key constraints:")
            for table_name in ['component', 'out2comp']:
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fks = cursor.fetchall()
                if fks:
                    print(f"   {table_name}:")
                    for fk in fks:
                        print(f"     - {fk[3]} -> {fk[2]}.{fk[4]}")
                else:
                    print(f"   {table_name}: No foreign keys")
                
            conn.close()
            
            # Step 6: Seed initial data
            print(f"\n🌱 Seeding initial data...")
            from services.seed_data import seed_initial_data
            with Session(engine) as session:
                seed_initial_data(session)
            print(f"✅ Seeded initial data")
            
            # Step 7: Verify seeded data
            print(f"\n📊 Verifying seeded data:")
            with Session(engine) as session:
                from sqlmodel import select
                
                vendors = session.exec(select(Vendor)).all()
                pieces = session.exec(select(Piece)).all()
                components = session.exec(select(Component)).all()
                outfits = session.exec(select(Outfit)).all()
                
                print(f"   Vendors: {len(vendors)}")
                print(f"   Pieces: {len(pieces)}")
                print(f"   Components: {len(components)}")
                print(f"   Outfits: {len(outfits)}")
                
                if vendors:
                    print(f"   Sample vendor: {vendors[0].name}")
                if pieces:
                    print(f"   Sample piece: {pieces[0].name}")
            
            print(f"\n🎉 Database recreation complete!")
            
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def verify_database_integrity():
    """Verify the recreated database has proper structure and data."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_file = "outfit_manager.db"
        
        if not os.path.exists(db_file):
            print("❌ Database file not found for verification")
            return
        
        print(f"\n🔍 VERIFYING DATABASE INTEGRITY")
        print("=" * 40)
        
        import sqlite3
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        try:
            # Check table structure
            expected_tables = ['vendor', 'piece', 'component', 'outfit', 'out2comp']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            actual_tables = [row[0] for row in cursor.fetchall()]
            
            print(f"Expected tables: {expected_tables}")
            print(f"Actual tables: {actual_tables}")
            
            missing_tables = set(expected_tables) - set(actual_tables)
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
            else:
                print(f"✅ All expected tables present")
            
            # Check specific column requirements
            critical_checks = [
                ('component', 'pieceid'),
                ('outfit', 'score')
            ]
            
            for table, column in critical_checks:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                if column in columns:
                    print(f"✅ {table}.{column} present")
                else:
                    print(f"❌ {table}.{column} MISSING")
            
            # Check that vendorid is NOT in outfit
            cursor.execute("PRAGMA table_info(outfit)")
            outfit_columns = [col[1] for col in cursor.fetchall()]
            if 'vendorid' not in outfit_columns:
                print(f"✅ outfit.vendorid correctly absent")
            else:
                print(f"❌ outfit.vendorid incorrectly present")
            
            # Test data insertion
            print(f"\n🧪 Testing data insertion:")
            
            # Insert test vendor
            cursor.execute("INSERT INTO vendor (name, description) VALUES (?, ?)", 
                          ("Test Vendor", "Test Description"))
            vendor_id = cursor.lastrowid
            print(f"✅ Test vendor inserted with ID {vendor_id}")
            
            # Insert test piece
            cursor.execute("INSERT INTO piece (name, description) VALUES (?, ?)", 
                          ("Test Piece", "Test Description"))
            piece_id = cursor.lastrowid
            print(f"✅ Test piece inserted with ID {piece_id}")
            
            # Insert test component with pieceid
            cursor.execute("""
                INSERT INTO component (name, brand, cost, vendorid, pieceid) 
                VALUES (?, ?, ?, ?, ?)
            """, ("Test Component", "Test Brand", 1000, vendor_id, piece_id))
            component_id = cursor.lastrowid
            print(f"✅ Test component inserted with ID {component_id}")
            
            # Insert test outfit with score
            cursor.execute("""
                INSERT INTO outfit (name, description, totalcost, score) 
                VALUES (?, ?, ?, ?)
            """, ("Test Outfit", "Test Description", 1000, 5))
            outfit_id = cursor.lastrowid
            print(f"✅ Test outfit inserted with ID {outfit_id} and score 5")
            
            # Insert test relationship
            cursor.execute("INSERT INTO out2comp (outid, comid) VALUES (?, ?)", 
                          (outfit_id, component_id))
            print(f"✅ Test outfit-component relationship created")
            
            # Verify insertions
            cursor.execute("SELECT COUNT(*) FROM component WHERE pieceid IS NOT NULL")
            components_with_pieces = cursor.fetchone()[0]
            print(f"✅ {components_with_pieces} components have piece references")
            
            cursor.execute("SELECT COUNT(*) FROM outfit WHERE score > 0")
            outfits_with_scores = cursor.fetchone()[0]
            print(f"✅ {outfits_with_scores} outfits have positive scores")
            
            # Clean up test data
            conn.rollback()  # This will undo our test insertions
            print(f"✅ Test data cleaned up")
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    force_recreate_database()
    verify_database_integrity()