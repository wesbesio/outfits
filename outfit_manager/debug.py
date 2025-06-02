# File: debug.py
# Revision: 1.0 - Project validation script

import os
from pathlib import Path
import importlib.util

def check_file_structure():
    """Check if all required files and directories exist."""
    required_structure = [
        "main.py",
        "requirements.txt",
        "models/__init__.py",
        "models/database.py",
        "routers/__init__.py",
        "routers/components.py",
        "routers/outfits.py", 
        "routers/vendors.py",
        "routers/pieces.py",
        "routers/images.py",
        "services/__init__.py",
        "services/image_service.py",
        "services/seed_data.py",
        "templates/base.html",
        "templates/components/list.html",
        "templates/components/list_content.html",
        "templates/components/detail.html",
        "templates/components/detail_content.html",
        "templates/outfits/list.html",
        "templates/outfits/list_content.html",
        "templates/outfits/detail.html",
        "templates/outfits/detail_content.html",
        "templates/forms/component_form.html",
        "templates/forms/component_form_content.html",
        "templates/forms/outfit_form.html",
        "templates/forms/outfit_form_content.html",
        "templates/forms/vendor_form.html",
        "templates/forms/vendor_form_content.html",
        "templates/partials/component_cards.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/vendor_options.html",
        "templates/partials/piece_options.html",
        "static/css/main.css",
        "static/js/main.js",
        "static/js/form-error-handler.js"
    ]
    
    missing_files = []
    for file_path in required_structure:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_python_imports():
    """Check if Python modules can be imported."""
    modules_to_check = [
        "models",
        "models.database",
        "routers.components",
        "routers.outfits",
        "services.image_service"
    ]
    
    failed_imports = []
    for module_name in modules_to_check:
        try:
            if Path(f"{module_name.replace('.', '/')}.py").exists():
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    f"{module_name.replace('.', '/')}.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {module_name} imports successfully")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name} failed to import: {e}")
    
    return len(failed_imports) == 0

def check_template_structure():
    """Check if templates have proper structure."""
    print("\n📋 Template Structure Check:")
    
    base_template = Path("templates/base.html")
    if base_template.exists():
        content = base_template.read_text()
        if "htmx.org" in content:
            print("✅ Base template includes HTMX")
        else:
            print("❌ Base template missing HTMX")
            
        if "main-content" in content:
            print("✅ Base template has main-content div")
        else:
            print("❌ Base template missing main-content div")
    else:
        print("❌ Base template not found")

def main():
    """Run all validation checks."""
    print("🔍 Outfit Manager Project Validation\n")
    
    print("📁 File Structure Check:")
    structure_ok = check_file_structure()
    
    print("\n🐍 Python Import Check:")
    imports_ok = check_python_imports()
    
    check_template_structure()
    
    print("\n" + "="*50)
    if structure_ok and imports_ok:
        print("🎉 Project validation successful!")
        print("✅ Ready for Phase 1 implementation")
    else:
        print("⚠️  Project validation failed")
        print("❌ Fix issues before proceeding")

if __name__ == "__main__":
    main()
