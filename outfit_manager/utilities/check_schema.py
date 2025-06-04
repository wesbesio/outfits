# File: utilities/check_schema.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

def check_database_schema():
    """Check the current database schema to diagnose missing columns."""
    # Change to parent directory for database operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        db_path = Path("outfit_manager.db")
        
        print(f"📁 Working directory: {os.getcwd()}")
        
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
                
            print("\n" + "=" * 50)
            print("🎯 EXPECTED vs ACTUAL for Outfit table:")
            
            expected_outfit_columns = [
                "outid", "name", "description", "notes", "totalcost", 
                "score", "image", "active", "flag"
            ]
            
            cursor.execute("PRAGMA table_info(outfit)")
            actual_outfit_columns = [col[1] for col in cursor.fetchall()]
            
            print(f"   Expected: {expected_outfit_columns}")
            print(f"   Actual:   {actual_outfit_columns}")
            
            missing_outfit = set(expected_outfit_columns) - set(actual_outfit_columns)
            extra_outfit = set(actual_outfit_columns) - set(expected_outfit_columns)
            
            if missing_outfit:
                print(f"   ❌ Missing: {list(missing_outfit)}")
            if extra_outfit:
                print(f"   ➕ Extra:   {list(extra_outfit)}")
            if not missing_outfit and not extra_outfit:
                print("   ✅ Schema matches expected structure")
                
            # Check foreign key relationships
            print("\n" + "=" * 50)
            print("🔗 FOREIGN KEY RELATIONSHIPS:")
            
            for table_name in ['component', 'outfit', 'out2comp']:
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fks = cursor.fetchall()
                
                if fks:
                    print(f"\n   {table_name} foreign keys:")
                    for fk in fks:
                        print(f"     - {fk[3]} -> {fk[2]}.{fk[4]}")
                else:
                    print(f"\n   {table_name}: No foreign keys")
                    
            # Check indexes
            print("\n" + "=" * 50)
            print("📇 INDEXES:")
            
            cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
            indexes = cursor.fetchall()
            
            if indexes:
                for idx in indexes:
                    print(f"   {idx[0]} on {idx[1]}")
            else:
                print("   No custom indexes found")
                
        except Exception as e:
            print(f"❌ Error checking schema: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def check_data_integrity():
    """Check data integrity and relationships."""
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
            print("\n" + "=" * 50)
            print("🔍 DATA INTEGRITY CHECK:")
            
            # Count records in each table
            tables = ['vendor', 'piece', 'component', 'outfit', 'out2comp']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   {table}: {count} records")
                    
                    # Check active records
                    if table in ['vendor', 'piece', 'component', 'outfit', 'out2comp']:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE active = 1")
                        active_count = cursor.fetchone()[0]
                        print(f"     Active: {active_count}")
                except sqlite3.OperationalError as e:
                    print(f"   {table}: Error - {e}")
            
            # Check orphaned relationships
            print(f"\n🔗 RELATIONSHIP INTEGRITY:")
            
            # Components with invalid vendor references
            cursor.execute("""
                SELECT COUNT(*) FROM component 
                WHERE vendorid IS NOT NULL 
                AND vendorid NOT IN (SELECT venid FROM vendor)
            """)
            orphaned_vendor_refs = cursor.fetchone()[0]
            if orphaned_vendor_refs > 0:
                print(f"   ❌ {orphaned_vendor_refs} components with invalid vendor references")
            else:
                print(f"   ✅ All component-vendor relationships valid")
            
            # Components with invalid piece references
            cursor.execute("""
                SELECT COUNT(*) FROM component 
                WHERE pieceid IS NOT NULL 
                AND pieceid NOT IN (SELECT piecid FROM piece)
            """)
            orphaned_piece_refs = cursor.fetchone()[0]
            if orphaned_piece_refs > 0:
                print(f"   ❌ {orphaned_piece_refs} components with invalid piece references")
            else:
                print(f"   ✅ All component-piece relationships valid")
            
            # Out2Comp with invalid outfit references
            cursor.execute("""
                SELECT COUNT(*) FROM out2comp 
                WHERE outid NOT IN (SELECT outid FROM outfit)
            """)
            orphaned_outfit_refs = cursor.fetchone()[0]
            if orphaned_outfit_refs > 0:
                print(f"   ❌ {orphaned_outfit_refs} out2comp records with invalid outfit references")
            else:
                print(f"   ✅ All out2comp-outfit relationships valid")
            
            # Out2Comp with invalid component references
            cursor.execute("""
                SELECT COUNT(*) FROM out2comp 
                WHERE comid NOT IN (SELECT comid FROM component)
            """)
            orphaned_comp_refs = cursor.fetchone()[0]
            if orphaned_comp_refs > 0:
                print(f"   ❌ {orphaned_comp_refs} out2comp records with invalid component references")
            else:
                print(f"   ✅ All out2comp-component relationships valid")
                
        except Exception as e:
            print(f"❌ Error checking data integrity: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def check_score_functionality():
    """Check score field functionality and statistics."""
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
            print("\n" + "=" * 50)
            print("🎯 SCORE FUNCTIONALITY CHECK:")
            
            # Check if score field exists
            cursor.execute("PRAGMA table_info(outfit)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'score' not in column_names:
                print("   ⚠️  Score field not found in outfit table")
                print("   💡 Run utilities/add_score_field.py to add it")
                return
            
            print("   ✅ Score field found in outfit table")
            
            # Score statistics
            cursor.execute("SELECT COUNT(*) FROM outfit WHERE active = 1")
            total_outfits = cursor.fetchone()[0]
            
            if total_outfits == 0:
                print("   ℹ️  No active outfits found")
                return
            
            print(f"   📊 Total active outfits: {total_outfits}")
            
            # Score distribution
            cursor.execute("""
                SELECT 
                    MIN(score) as min_score,
                    MAX(score) as max_score,
                    AVG(score) as avg_score,
                    COUNT(CASE WHEN score = 0 THEN 1 END) as zero_scores,
                    COUNT(CASE WHEN score > 0 THEN 1 END) as positive_scores
                FROM outfit 
                WHERE active = 1
            """)
            stats = cursor.fetchone()
            
            min_score, max_score, avg_score, zero_scores, positive_scores = stats
            
            print(f"   📈 Score Statistics:")
            print(f"     - Range: {min_score} to {max_score}")
            print(f"     - Average: {avg_score:.1f}")
            print(f"     - Zero scores: {zero_scores}")
            print(f"     - Positive scores: {positive_scores}")
            
            # Score distribution by ranges
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN score = 0 THEN 1 END) as zero,
                    COUNT(CASE WHEN score BETWEEN 1 AND 2 THEN 1 END) as low,
                    COUNT(CASE WHEN score BETWEEN 3 AND 4 THEN 1 END) as medium,
                    COUNT(CASE WHEN score >= 5 THEN 1 END) as high
                FROM outfit 
                WHERE active = 1
            """)
            distribution = cursor.fetchone()
            zero, low, medium, high = distribution
            
            print(f"   🎨 Score Distribution:")
            print(f"     - Zero (0): {zero} outfits")
            print(f"     - Low (1-2): {low} outfits")
            print(f"     - Medium (3-4): {medium} outfits")
            print(f"     - High (5+): {high} outfits")
            
            # Top scored outfits
            cursor.execute("""
                SELECT name, score 
                FROM outfit 
                WHERE active = 1 AND score > 0
                ORDER BY score DESC, name ASC 
                LIMIT 5
            """)
            top_outfits = cursor.fetchall()
            
            if top_outfits:
                print(f"   🏆 Top Scored Outfits:")
                for name, score in top_outfits:
                    print(f"     - {name}: {score}")
            
        except Exception as e:
            print(f"❌ Error checking score functionality: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def check_legacy_issues():
    """Check for legacy issues that might need fixing."""
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
            print("\n" + "=" * 50)
            print("🔧 LEGACY ISSUES CHECK:")
            
            # Check for vendorid in outfit table (should be removed)
            cursor.execute("PRAGMA table_info(outfit)")
            outfit_columns = [col[1] for col in cursor.fetchall()]
            
            if 'vendorid' in outfit_columns:
                print("   ⚠️  outfit table still contains vendorid column")
                print("   💡 Run utilities/remove_vendors_from_outfits.py to remove it")
            else:
                print("   ✅ outfit table correctly excludes vendorid")
            
            # Check for missing pieceid in component table
            cursor.execute("PRAGMA table_info(component)")
            component_columns = [col[1] for col in cursor.fetchall()]
            
            if 'pieceid' not in component_columns:
                print("   ⚠️  component table missing pieceid column")
                print("   💡 Run utilities/force_recreate_db.py to fix schema")
            else:
                print("   ✅ component table correctly includes pieceid")
            
            # Check for missing score in outfit table
            if 'score' not in outfit_columns:
                print("   ⚠️  outfit table missing score column")
                print("   💡 Run utilities/add_score_field.py to add it")
            else:
                print("   ✅ outfit table correctly includes score")
            
            # Check for unused tables or columns
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = {'vendor', 'piece', 'component', 'outfit', 'out2comp'}
            actual_tables = set(all_tables)
            
            unexpected_tables = actual_tables - expected_tables
            if unexpected_tables:
                print(f"   ⚠️  Unexpected tables found: {list(unexpected_tables)}")
            else:
                print("   ✅ No unexpected tables found")
            
            # Check for backup files in main directory
            backup_files = [
                "outfit_manager_backup.db",
                "outfit_manager_backup_before_score.db"
            ]
            
            found_backups = []
            for backup_file in backup_files:
                if os.path.exists(backup_file):
                    size = os.path.getsize(backup_file)
                    found_backups.append(f"{backup_file} ({size} bytes)")
            
            if found_backups:
                print(f"   ℹ️  Backup files found:")
                for backup in found_backups:
                    print(f"     - {backup}")
            
        except Exception as e:
            print(f"❌ Error checking legacy issues: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def generate_schema_report():
    """Generate a comprehensive schema report."""
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
            print("\n" + "=" * 50)
            print("📋 COMPREHENSIVE SCHEMA REPORT:")
            
            # Database file info
            db_size = os.path.getsize(db_path)
            print(f"   📁 Database file: {db_path}")
            print(f"   📊 File size: {db_size:,} bytes ({db_size/1024:.1f} KB)")
            
            # Table summary
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"   📋 Tables: {len(tables)} ({', '.join(tables)})")
            
            # Record counts
            total_records = 0
            print(f"   📊 Record counts:")
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    total_records += count
                    print(f"     - {table}: {count:,}")
                except sqlite3.OperationalError:
                    print(f"     - {table}: Error reading")
            
            print(f"   📊 Total records: {total_records:,}")
            
            # Index count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
            index_count = cursor.fetchone()[0]
            print(f"   📇 Custom indexes: {index_count}")
            
            # Foreign key count
            fk_count = 0
            for table in tables:
                cursor.execute(f"PRAGMA foreign_key_list({table})")
                fk_count += len(cursor.fetchall())
            print(f"   🔗 Foreign key relationships: {fk_count}")
            
            # Schema version check
            print(f"\n   🎯 Schema Validation:")
            
            # Check critical fields
            critical_checks = [
                ("component", "pieceid", "Component-Piece relationship"),
                ("outfit", "score", "Outfit scoring system"),
            ]
            
            schema_valid = True
            for table, column, description in critical_checks:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if column in columns:
                    print(f"     ✅ {description}: Present")
                else:
                    print(f"     ❌ {description}: Missing")
                    schema_valid = False
            
            # Check that vendorid is NOT in outfit
            cursor.execute("PRAGMA table_info(outfit)")
            outfit_columns = [col[1] for col in cursor.fetchall()]
            
            if 'vendorid' not in outfit_columns:
                print(f"     ✅ Outfit-Vendor separation: Correct")
            else:
                print(f"     ❌ Outfit-Vendor separation: vendorid still present")
                schema_valid = False
            
            # Overall schema status
            if schema_valid:
                print(f"\n   🎉 SCHEMA STATUS: ✅ VALID")
                print(f"     All expected fields are present and correct")
            else:
                print(f"\n   ⚠️  SCHEMA STATUS: ❌ NEEDS ATTENTION")
                print(f"     Some expected fields are missing or incorrect")
                print(f"     Check the utilities folder for migration scripts")
            
        except Exception as e:
            print(f"❌ Error generating schema report: {e}")
        finally:
            conn.close()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def run_complete_analysis():
    """Run all analysis functions in sequence."""
    print("🔍 COMPLETE DATABASE SCHEMA ANALYSIS")
    print("=" * 60)
    
    analysis_functions = [
        ("Schema Structure", check_database_schema),
        ("Data Integrity", check_data_integrity),
        ("Score Functionality", check_score_functionality),
        ("Legacy Issues", check_legacy_issues),
        ("Schema Report", generate_schema_report)
    ]
    
    for analysis_name, analysis_func in analysis_functions:
        try:
            print(f"\n🔬 Running {analysis_name} Analysis...")
            analysis_func()
        except Exception as e:
            print(f"❌ {analysis_name} analysis failed: {e}")
    
    print(f"\n🎯 ANALYSIS COMPLETE")
    print("=" * 30)
    print("📝 Review the output above for any issues that need attention")
    print("🔧 Use the appropriate utilities scripts to fix any problems found")

if __name__ == "__main__":
    # Can run individual checks or complete analysis
    import sys
    
    if len(sys.argv) > 1:
        check_arg = sys.argv[1].lower()
        
        if check_arg == "schema":
            check_database_schema()
        elif check_arg == "integrity":
            check_data_integrity()
        elif check_arg == "score":
            check_score_functionality()
        elif check_arg == "legacy":
            check_legacy_issues()
        elif check_arg == "report":
            generate_schema_report()
        else:
            print("Available options: schema, integrity, score, legacy, report, or run without arguments for complete analysis")
    else:
        # Run complete analysis
        run_complete_analysis()