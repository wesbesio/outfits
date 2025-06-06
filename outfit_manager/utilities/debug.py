# File: utilities/debug.py
# Revision: 6.0 - Complete project validation with vendor/piece management and search error testing

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import importlib.util

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

def check_file_exists(file_path: str) -> bool:
    """Check if a file exists."""
    return Path(file_path).exists()

def check_directory_structure() -> Dict[str, bool]:
    """Check if all required directories exist."""
    print("🔍 CHECKING DIRECTORY STRUCTURE")
    print("=" * 40)
    
    required_directories = [
        "models",
        "routers", 
        "services",
        "utilities",
        "static",
        "static/css",
        "static/js",
        "static/images",
        "templates",
        "templates/components",
        "templates/outfits",
        "templates/vendors",
        "templates/pieces",
        "templates/forms",
        "templates/partials",
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        results = {}
        for directory in required_directories:
            exists = Path(directory).exists()
            results[directory] = exists
            status = "✅" if exists else "❌"
            print(f"   {status} {directory}")
        
        missing_dirs = [d for d, exists in results.items() if not exists]
        if missing_dirs:
            print(f"\n⚠️  Missing directories: {missing_dirs}")
            print("💡 Run 'python utilities/setup_directories.py' to create them")
        else:
            print(f"\n✅ All required directories exist!")
        
        return results
    finally:
        os.chdir(original_dir)

def check_core_files() -> Dict[str, bool]:
    """Check if all core application files exist."""
    print(f"\n🔍 CHECKING CORE FILES")
    print("=" * 25)
    
    core_files = [
        "main.py",
        "requirements.txt",
        "models/__init__.py",
        "models/database.py",
        "routers/components.py",
        "routers/images.py",
        "routers/outfits.py",
        "routers/vendors.py",
        "routers/pieces.py",
        "services/__init__.py",
        "services/image_service.py",
        "services/seed_data.py",
        "services/template_service.py",
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        results = {}
        for file_path in core_files:
            exists = check_file_exists(file_path)
            results[file_path] = exists
            status = "✅" if exists else "❌"
            print(f"   {status} {file_path}")
        
        missing_files = [f for f, exists in results.items() if not exists]
        if missing_files:
            print(f"\n⚠️  Missing core files: {missing_files}")
        else:
            print(f"\n✅ All core files exist!")
        
        return results
    finally:
        os.chdir(original_dir)

def check_template_structure() -> Dict[str, bool]:
    """Check if all required templates exist."""
    print(f"\n🔍 CHECKING TEMPLATE STRUCTURE")
    print("=" * 30)
    
    required_templates = [
        # Base template
        "templates/base.html",
        
        # Component templates
        "templates/components/list.html",
        "templates/components/list_main_content.html",
        "templates/components/list_content.html",
        "templates/components/detail.html",
        "templates/components/detail_main_content.html",
        "templates/components/detail_content.html",
        
        # Outfit templates
        "templates/outfits/list.html",
        "templates/outfits/list_main_content.html", 
        "templates/outfits/list_content.html",
        "templates/outfits/detail.html",
        "templates/outfits/detail_main_content.html",
        "templates/outfits/detail_content.html",
        
        # Vendor templates
        "templates/vendors/list.html",
        "templates/vendors/list_main_content.html",
        "templates/vendors/list_content.html",
        "templates/vendors/detail.html",
        "templates/vendors/detail_main_content.html",
        "templates/vendors/detail_content.html",
        
        # Piece templates
        "templates/pieces/list.html",
        "templates/pieces/list_main_content.html",
        "templates/pieces/list_content.html",
        "templates/pieces/detail.html",
        "templates/pieces/detail_main_content.html",
        "templates/pieces/detail_content.html",
        
        # Form templates
        "templates/forms/component_form.html",
        "templates/forms/component_form_content.html",
        "templates/forms/outfit_form.html",
        "templates/forms/outfit_form_content.html",
        "templates/forms/vendor_form.html",
        "templates/forms/vendor_form_content.html",
        "templates/forms/piece_form.html",
        "templates/forms/piece_form_content.html",
        
        # Partial templates
        "templates/partials/component_cards.html",
        "templates/partials/component_checkboxes.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/vendor_cards.html",
        "templates/partials/piece_cards.html",
        "templates/partials/vendor_options.html",
        "templates/partials/piece_options.html",
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        results = {}
        for template_path in required_templates:
            exists = check_file_exists(template_path)
            results[template_path] = exists
            status = "✅" if exists else "❌"
            print(f"   {status} {template_path}")
        
        missing_templates = [t for t, exists in results.items() if not exists]
        if missing_templates:
            print(f"\n⚠️  Missing templates: {missing_templates}")
        else:
            print(f"\n✅ All required templates exist!")
        
        return results
    finally:
        os.chdir(original_dir)

def check_static_files() -> Dict[str, bool]:
    """Check if all required static files exist."""
    print(f"\n🔍 CHECKING STATIC FILES")
    print("=" * 25)
    
    static_files = [
        "static/css/main.css",
        "static/js/form-error-handler.js",
        "static/js/image-preview.js",
        "static/images/placeholder.svg",
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        results = {}
        for file_path in static_files:
            exists = check_file_exists(file_path)
            results[file_path] = exists
            status = "✅" if exists else "❌"
            print(f"   {status} {file_path}")
            
            # Check file size for non-empty files
            if exists:
                size = Path(file_path).stat().st_size
                print(f"      📊 {size} bytes")
        
        missing_files = [f for f, exists in results.items() if not exists]
        if missing_files:
            print(f"\n⚠️  Missing static files: {missing_files}")
        else:
            print(f"\n✅ All static files exist!")
        
        return results
    finally:
        os.chdir(original_dir)

def check_model_imports() -> bool:
    """Check if models can be imported successfully."""
    print(f"\n🔍 CHECKING MODEL IMPORTS")
    print("=" * 26)
    
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        # Try importing all models
        from models import Vendor, Piece, Component, Outfit, Out2Comp
        print("   ✅ All models imported successfully")
        
        # Check model attributes
        model_checks = [
            (Component, 'pieceid', 'Component-Piece relationship'),
            (Outfit, 'score', 'Outfit scoring system'),
        ]
        
        for model_class, attr_name, description in model_checks:
            if hasattr(model_class, '__annotations__') and attr_name in model_class.__annotations__:
                print(f"   ✅ {description}: {attr_name} field present")
            else:
                print(f"   ❌ {description}: {attr_name} field missing")
                return False
        
        # Check that vendorid is NOT in outfit
        if hasattr(Outfit, '__annotations__') and 'vendorid' not in Outfit.__annotations__:
            print(f"   ✅ Outfit-Vendor separation: vendorid correctly removed")
        else:
            print(f"   ❌ Outfit-Vendor separation: vendorid still present")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Model import failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def check_router_imports() -> bool:
    """Check if routers can be imported successfully."""
    print(f"\n🔍 CHECKING ROUTER IMPORTS")
    print("=" * 27)
    
    routers = [
        ("components", "routers.components"),
        ("images", "routers.images"), 
        ("outfits", "routers.outfits"),
        ("vendors", "routers.vendors"),
        ("pieces", "routers.pieces"),
    ]
    
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        for router_name, import_path in routers:
            try:
                spec = importlib.util.spec_from_file_location(router_name, f"routers/{router_name}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'router'):
                    print(f"   ✅ {router_name}.py - router object found")
                else:
                    print(f"   ❌ {router_name}.py - router object missing")
                    return False
                    
            except Exception as e:
                print(f"   ❌ {router_name}.py - import failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Router import check failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def check_main_app_structure() -> bool:
    """Check main.py app structure."""
    print(f"\n🔍 CHECKING MAIN APP STRUCTURE")
    print("=" * 32)
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        if not check_file_exists("main.py"):
            print("   ❌ main.py not found")
            return False
        
        with open("main.py", 'r') as f:
            main_content = f.read()
        
        # Check for required imports
        required_imports = [
            "from routers import components",
            "from routers import images", 
            "from routers import outfits",
            "from routers import vendors",
            "from routers import pieces",
        ]
        
        for import_line in required_imports:
            if import_line in main_content:
                print(f"   ✅ {import_line}")
            else:
                print(f"   ❌ Missing: {import_line}")
                return False
        
        # Check for router includes
        required_includes = [
            "app.include_router(components.router",
            "app.include_router(images.router",
            "app.include_router(outfits.router", 
            "app.include_router(vendors.router",
            "app.include_router(pieces.router",
        ]
        
        for include_line in required_includes:
            if include_line in main_content:
                print(f"   ✅ {include_line}")
            else:
                print(f"   ❌ Missing: {include_line}")
                return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Main app structure check failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

def check_score_functionality() -> bool:
    """Check score functionality in templates and CSS."""
    print(f"\n🔍 CHECKING SCORE FUNCTIONALITY")
    print("=" * 31)
    
    score_checks = [
        ("templates/outfits/detail_content.html", "score-display", "Score display container"),
        ("templates/outfits/detail_content.html", "score-controls", "Score control buttons"),
        ("templates/partials/outfit_cards.html", "score-badge", "Score badge in cards"),
        ("templates/forms/outfit_form_content.html", 'name="score"', "Score input field"),
        ("static/css/main.css", ".score-display", "Score display styles"),
        ("static/css/main.css", ".btn-score-plus", "Score button styles"),
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        all_good = True
        for file_path, search_term, description in score_checks:
            if check_file_exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if search_term in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - missing '{search_term}'")
                    all_good = False
            else:
                print(f"   ❌ {description} - file missing: {file_path}")
                all_good = False
        
        return all_good
    finally:
        os.chdir(original_dir)

def check_vendor_piece_management() -> bool:
    """Check vendor and piece management functionality."""
    print(f"\n🔍 CHECKING VENDOR/PIECE MANAGEMENT")
    print("=" * 36)
    
    management_checks = [
        ("templates/base.html", "hamburger-menu", "Hamburger menu"),
        ("templates/base.html", "🏪", "Vendor icon in navigation"),
        ("templates/base.html", "🧩", "Piece icon in navigation"),
        ("templates/partials/vendor_cards.html", "🏪", "Vendor card icon"),
        ("templates/partials/piece_cards.html", "🧩", "Piece card icon"),
        ("templates/partials/vendor_options.html", "Manage Vendors", "Vendor management link"),
        ("templates/partials/piece_options.html", "Manage Piece Types", "Piece management link"),
        ("static/css/main.css", ".hamburger-menu", "Hamburger menu styles"),
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        all_good = True
        for file_path, search_term, description in management_checks:
            if check_file_exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if search_term in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - missing '{search_term}'")
                    all_good = False
            else:
                print(f"   ❌ {description} - file missing: {file_path}")
                all_good = False
        
        return all_good
    finally:
        os.chdir(original_dir)

def check_htmx_patterns() -> bool:
    """Check for proper HTMX patterns and avoid auto-loading issues."""
    print(f"\n🔍 CHECKING HTMX PATTERNS")
    print("=" * 26)
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        # Check base template for HTMX script
        if check_file_exists("templates/base.html"):
            with open("templates/base.html", 'r') as f:
                base_content = f.read()
            
            if "htmx.org" in base_content:
                print("   ✅ HTMX script included in base template")
            else:
                print("   ❌ HTMX script missing from base template")
                return False
        
        # Check for problematic auto-loading patterns
        template_files = [
            "templates/components/list_main_content.html",
            "templates/outfits/list_main_content.html",
            "templates/vendors/list_main_content.html", 
            "templates/pieces/list_main_content.html",
        ]
        
        auto_load_issues = []
        for template_file in template_files:
            if check_file_exists(template_file):
                with open(template_file, 'r') as f:
                    content = f.read()
                
                # Check for hx-trigger="load" which can cause issues
                if 'hx-trigger="load"' in content:
                    auto_load_issues.append(template_file)
        
        if auto_load_issues:
            print(f"   ⚠️  Auto-loading patterns found in: {auto_load_issues}")
            print("   💡 Consider using manual loading to avoid form issues")
        else:
            print("   ✅ No problematic auto-loading patterns found")
        
        return True
    finally:
        os.chdir(original_dir)

def check_error_handling() -> bool:
    """Check error handling implementation."""
    print(f"\n🔍 CHECKING ERROR HANDLING")
    print("=" * 27)
    
    error_checks = [
        ("static/js/form-error-handler.js", "htmx:responseError", "HTMX error handling"),
        ("templates/base.html", "global-error-toast", "Global error toast"),
        ("routers/components.py", "safe_int_conversion", "Safe parameter conversion"),
        ("routers/outfits.py", "try:", "Try-catch blocks"),
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        all_good = True
        for file_path, search_term, description in error_checks:
            if check_file_exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if search_term in content:
                    print(f"   ✅ {description}")
                else:
                    print(f"   ❌ {description} - missing '{search_term}'")
                    all_good = False
            else:
                print(f"   ❌ {description} - file missing: {file_path}")
                all_good = False
        
        return all_good
    finally:
        os.chdir(original_dir)

def check_database_migration() -> bool:
    """Check database migration utilities."""
    print(f"\n🔍 CHECKING DATABASE MIGRATION")
    print("=" * 31)
    
    migration_files = [
        "utilities/add_score_field.py",
        "utilities/check_schema.py",
        "utilities/force_recreate_db.py",
    ]
    
    # Change to parent directory for validation
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        all_good = True
        for file_path in migration_files:
            if check_file_exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} - missing")
                all_good = False
        
        return all_good
    finally:
        os.chdir(original_dir)

def generate_summary_report(checks: Dict[str, bool]) -> None:
    """Generate a summary report of all checks."""
    print(f"\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY REPORT")
    print("=" * 60)
    
    total_checks = len(checks)
    passed_checks = sum(1 for result in checks.values() if result)
    failed_checks = total_checks - passed_checks
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {passed_checks}/{total_checks}")
    print(f"   ❌ Failed: {failed_checks}/{total_checks}")
    
    if failed_checks == 0:
        print(f"\n🎉 EXCELLENT! All validation checks passed!")
        print(f"🚀 Your Outfit Manager application is ready to run!")
        print(f"💡 Start with: uvicorn main:app --reload")
    else:
        print(f"\n⚠️  Some checks failed. Please review the issues above.")
        print(f"🔧 Common fixes:")
        print(f"   - Run 'python utilities/setup_directories.py' for missing directories")
        print(f"   - Check file paths and naming conventions")
        print(f"   - Verify all imports and router configurations")
        
        failed_categories = [category for category, result in checks.items() if not result]
        print(f"📝 Failed categories: {', '.join(failed_categories)}")

def run_validation() -> bool:
    """Run all validation checks."""
    print("🔍 OUTFIT MANAGER PROJECT VALIDATION")
    print("=" * 50)
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📁 Project root: {Path(__file__).parent.parent}")
    
    checks = {}
    
    # Run all validation checks
    dir_results = check_directory_structure()
    checks["Directory Structure"] = all(dir_results.values())
    
    core_results = check_core_files()
    checks["Core Files"] = all(core_results.values())
    
    template_results = check_template_structure()
    checks["Template Structure"] = all(template_results.values())
    
    static_results = check_static_files()
    checks["Static Files"] = all(static_results.values())
    
    checks["Model Imports"] = check_model_imports()
    checks["Router Imports"] = check_router_imports()
    checks["Main App Structure"] = check_main_app_structure()
    checks["Score Functionality"] = check_score_functionality()
    checks["Vendor/Piece Management"] = check_vendor_piece_management()
    checks["HTMX Patterns"] = check_htmx_patterns()
    checks["Error Handling"] = check_error_handling()
    checks["Database Migration"] = check_database_migration()
    
    # Generate summary report
    generate_summary_report(checks)
    
    return all(checks.values())

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)