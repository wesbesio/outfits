# Quick debug script to check if templates exist
import os

def check_template_structure():
    """Check if all required templates and directories exist"""
    base_dir = "."
    
    required_structure = [
        # Core directories
        "templates/",
        "templates/outfits/",
        "templates/components/", 
        "templates/partials/",
        "static/",
        "static/css/",
        "static/js/",
        "models/",
        "routers/",
        "services/",
        
        # Template files - Base
        "templates/base.html",
        
        # Template files - Outfits
        "templates/outfits/list.html", 
        "templates/outfits/detail.html",
        
        # Template files - Components
        "templates/components/list.html",
        "templates/components/detail.html",
        
        # Partial templates (HTMX)
        "templates/partials/component_form.html",
        "templates/partials/outfit_form.html",
        "templates/partials/vendor_form.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/component_cards.html",
        "templates/partials/vendor_options.html",
        "templates/partials/piece_options.html",
        "templates/partials/add_component_form.html",
        
        # Static files
        "static/css/main.css",
        "static/js/main.js",
        "static/js/image-upload.js",
        
        # Python files - Core
        "main.py",
        "requirements.txt",
        "debug.py",
        
        # Models
        "models/__init__.py",
        "models/database.py",
        
        # Routers
        "routers/__init__.py",
        "routers/outfits.py",
        "routers/components.py",
        "routers/vendors.py",
        "routers/pieces.py",
        "routers/images.py",
        "routers/web_routes.py",
        
        # Services
        "services/__init__.py",
        "services/image_service.py",
        "services/seed_data.py",
        
        # Database (auto-generated)
        "outfit_manager.db",
        
        # Optional directories that might exist
        "__pycache__/",
        ".git/",
        ".gitignore",
        "README.md",
        
        # Virtual environment (if present)
        "venv/",
        "env/",
        
        # IDE files (if present)  
        ".vscode/",
        ".idea/",
        
        # Python cache
        "models/__pycache__/",
        "routers/__pycache__/",
        "services/__pycache__/",
        
        # Logs (if any)
        "logs/",
        "app.log",
        
        # Config files (if any)
        ".env",
        "config.py",
        "alembic.ini",
        "alembic/",
    ]
    
    missing = []
    existing = []
    
    for path in required_structure:
        full_path = os.path.join(base_dir, path)
        if not os.path.exists(full_path):
            missing.append(path)
        else:
            existing.append(path)
            
    print(f"📊 Structure Check Results:")
    print(f"✅ Existing: {len(existing)}/{len(required_structure)} files/directories")
    print(f"❌ Missing: {len(missing)}/{len(required_structure)} files/directories")
    print()
    
    if missing:
        print("❌ Missing files/directories:")
        
        # Group by type
        missing_dirs = [item for item in missing if item.endswith('/')]
        missing_templates = [item for item in missing if 'templates/' in item and not item.endswith('/')]
        missing_static = [item for item in missing if 'static/' in item and not item.endswith('/')]
        missing_python = [item for item in missing if item.endswith('.py')]
        missing_other = [item for item in missing if item not in missing_dirs + missing_templates + missing_static + missing_python]
        
        if missing_dirs:
            print("\n📁 Missing Directories:")
            for item in missing_dirs:
                print(f"   - {item}")
                
        if missing_templates:
            print("\n📄 Missing Templates:")
            for item in missing_templates:
                print(f"   - {item}")
                
        if missing_static:
            print("\n🎨 Missing Static Files:")
            for item in missing_static:
                print(f"   - {item}")
                
        if missing_python:
            print("\n🐍 Missing Python Files:")
            for item in missing_python:
                print(f"   - {item}")
                
        if missing_other:
            print("\n📋 Missing Other Files:")
            for item in missing_other:
                print(f"   - {item}")
        
        print("\n🔧 Quick Fix Commands:")
        print("# Create missing directories:")
        if missing_dirs:
            dirs_to_create = " ".join([d.rstrip('/') for d in missing_dirs])
            print(f"mkdir -p {dirs_to_create}")
        
        print("\n# Create missing template files:")
        template_files = [f for f in missing_templates]
        for template in template_files:
            print(f"touch {template}")
            
        print("\n# Create missing static files:")
        static_files = [f for f in missing_static]
        for static in static_files:
            print(f"touch {static}")
            
        print("\n# Create missing Python files:")
        python_files = [f for f in missing_python]
        for py_file in python_files:
            print(f"touch {py_file}")
            
    else:
        print("🎉 All required files and directories exist!")
        
    print("\n" + "="*60)
    print("🔍 Priority Files to Create (if missing):")
    
    priority_files = [
        "templates/partials/component_form.html",
        "templates/partials/outfit_form.html", 
        "templates/partials/vendor_form.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/component_cards.html",
        "templates/base.html",
        "static/css/main.css",
        "static/js/main.js",
        "routers/pieces.py",
        "routers/web_routes.py",
        "main.py"
    ]
    
    priority_missing = [f for f in priority_files if f in missing]
    
    if priority_missing:
        print("❗ Critical missing files that will cause 422 errors:")
        for file in priority_missing:
            print(f"   - {file}")
    else:
        print("✅ All critical files exist!")

def check_file_sizes():
    """Check if files have content (not empty)"""
    print("\n" + "="*60)
    print("📏 File Size Check:")
    
    important_files = [
        "templates/base.html",
        "templates/partials/component_form.html",
        "templates/partials/outfit_form.html",
        "templates/partials/vendor_form.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/component_cards.html",
        "static/css/main.css",
        "static/js/main.js",
        "static/js/image-upload.js",
        "models/__init__.py",
        "routers/web_routes.py",
        "routers/pieces.py",
        "routers/components.py",
        "routers/outfits.py",
        "main.py",
        "services/seed_data.py"
    ]
    
    for file in important_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            if size == 0:
                print(f"⚠️  {file} - EMPTY (0 bytes)")
            elif size < 100:
                print(f"⚠️  {file} - Very small ({size} bytes)")
            else:
                print(f"✅ {file} - OK ({size} bytes)")
        else:
            print(f"❌ {file} - MISSING")

if __name__ == "__main__":
    check_template_structure()
    check_file_sizes()