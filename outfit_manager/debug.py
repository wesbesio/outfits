# File: debug.py
# Revision: 3.2 - Updated for image upload in creation forms

import os

def check_template_structure():
    """Check if all required files exist and identify legacy files to remove"""
    base_dir = "."
    
    # Updated required structure after image upload implementation
    required_structure = [
        # Core directories
        "templates/",
        "templates/forms/",           # Form directory
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
        
        # Template files - Forms
        "templates/forms/outfit_form.html",       # Full page form
        "templates/forms/component_form.html",    # Full page form
        "templates/forms/vendor_form.html",       # Full page form
        
        # Template files - Content-only templates for HTMX
        "templates/forms/outfit_form_content.html",      # 🆕 Content-only template
        "templates/forms/component_form_content.html",   # 🆕 Content-only template
        "templates/forms/vendor_form_content.html",      # 🆕 Content-only template
        "templates/outfits/list_content.html",           # 🆕 Content-only template
        "templates/components/list_content.html",        # 🆕 Content-only template
        
        # Template files - Views
        "templates/outfits/list.html", 
        "templates/outfits/detail.html",
        "templates/components/list.html",
        "templates/components/detail.html",
        
        # Partial templates (HTMX fragments only)
        "templates/partials/outfit_cards.html",
        "templates/partials/component_cards.html",
        "templates/partials/vendor_options.html",
        "templates/partials/piece_options.html",
        
        # Static files
        "static/css/main.css",
        "static/js/main.js",
        "static/js/image-upload.js",
        "static/js/simple-upload.js",     # 🆕 New file for form image upload
        
        # Python files - Core
        "main.py",
        "requirements.txt",
        "debug.py",
        
        # Models
        "models/__init__.py",
        "models/database.py",
        
        # Routers (Updated)
        "routers/__init__.py",
        "routers/outfits.py",       # Updated with HTMX redirects
        "routers/components.py",    # Updated with HTMX redirects
        "routers/vendors.py",       # Updated with HTMX redirects
        "routers/pieces.py",
        "routers/images.py",
        
        # Services
        "services/__init__.py",
        "services/image_service.py",
        "services/seed_data.py",
        
        # Database (auto-generated)
        "outfit_manager.db",
    ]
    
    # Legacy files that should be REMOVED after refactor
    legacy_files = [
        "templates/partials/outfit_form.html",         # ❌ Replaced by forms/outfit_form.html
        "templates/partials/component_form.html",      # ❌ Replaced by forms/component_form.html
        "templates/partials/vendor_form.html",         # ❌ Replaced by forms/vendor_form.html
        "templates/partials/add_component_form.html",  # ❌ No longer needed with new architecture
        "routers/web_routes.py",                       # ❌ Routes moved to main.py
        "static/js/form-image-upload.js",              # ❌ Replaced by simple-upload.js
    ]
    
    # Optional files/directories (OK if present or absent)
    optional_structure = [
        "__pycache__/",
        ".git/",
        ".gitignore",
        "README.md",
        "venv/",
        "env/",
        ".vscode/",
        ".idea/",
        "models/__pycache__/",
        "routers/__pycache__/",
        "services/__pycache__/",
        "logs/",
        "app.log",
        ".env",
        "config.py",
        "alembic.ini",
        "alembic/",
        # Empty model files (legacy, but harmless)
        "models/components.py",
        "models/outfits.py",
        "models/pieces.py",
        "models/relationships.py",
        "models/vendors.py",
    ]
    
    missing = []
    existing = []
    legacy_present = []
    
    # Check required files
    for path in required_structure:
        full_path = os.path.join(base_dir, path)
        if not os.path.exists(full_path):
            missing.append(path)
        else:
            existing.append(path)
    
    # Check for legacy files that should be removed
    for path in legacy_files:
        full_path = os.path.join(base_dir, path)
        if os.path.exists(full_path):
            legacy_present.append(path)
    
    # Print results
    print("🎯 OUTFIT MANAGER - FILE STRUCTURE CHECK")
    print("=" * 60)
    print(f"✅ Required files found: {len(existing)}/{len(required_structure)}")
    print(f"❌ Missing files: {len(missing)}")
    print(f"🗑️  Legacy files to remove: {len(legacy_present)}")
    print()
    
    # Show missing files
    if missing:
        print("❌ MISSING REQUIRED FILES:")
        
        # Group by type
        missing_dirs = [item for item in missing if item.endswith('/')]
        missing_forms = [item for item in missing if 'templates/forms/' in item]
        missing_content_templates = [item for item in missing if '_content.html' in item]
        missing_templates = [item for item in