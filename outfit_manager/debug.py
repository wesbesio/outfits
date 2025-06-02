# File: debug.py
# Revision: 3.3 - Enhanced template structure checks and error reporting

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
        "static/js/form-error-handler.js",# 🆕 New file for form error handling
        
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
        "static/js/basic-upload.js",                   # ❌ Replaced by simple-upload.js
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
        missing_templates = [item for item in missing if item.endswith('.html') and item not in missing_forms and item not in missing_content_templates]
        missing_js = [item for item in missing if item.endswith('.js')]
        missing_py = [item for item in missing if item.endswith('.py')]
        missing_other = [item for item in missing if item not in missing_dirs + missing_forms + missing_content_templates + missing_templates + missing_js + missing_py]
        
        if missing_dirs:
            print("\n📁 Missing Directories:")
            for item in missing_dirs:
                print(f"  - {item}")
        
        if missing_forms:
            print("\n📑 Missing Form Templates:")
            for item in missing_forms:
                print(f"  - {item}")
        
        if missing_content_templates:
            print("\n🔄 Missing HTMX Content Templates:")
            for item in missing_content_templates:
                print(f"  - {item}")
        
        if missing_templates:
            print("\n📄 Missing Templates:")
            for item in missing_templates:
                print(f"  - {item}")
        
        if missing_js:
            print("\n📜 Missing JavaScript Files:")
            for item in missing_js:
                print(f"  - {item}")
        
        if missing_py:
            print("\n🐍 Missing Python Files:")
            for item in missing_py:
                print(f"  - {item}")
        
        if missing_other:
            print("\n⚙️ Missing Other Files:")
            for item in missing_other:
                print(f"  - {item}")
    
    # Show legacy files
    if legacy_present:
        print("\n🗑️ LEGACY FILES TO REMOVE:")
        for item in legacy_present:
            print(f"  - {item}")
    
    # Additional checks for template integrity
    print("\n🔍 ADDITIONAL CHECKS:")
    
    # Check for any form templates without content versions
    form_templates = [path for path in existing if "templates/forms/" in path and not path.endswith("_content.html")]
    content_templates = [path for path in existing if "templates/forms/" in path and path.endswith("_content.html")]
    
    missing_content_pairs = []
    for form in form_templates:
        expected_content = form.replace(".html", "_content.html")
        if expected_content not in content_templates:
            missing_content_pairs.append((form, expected_content))
    
    if missing_content_pairs:
        print("\n⚠️ Form templates missing their content-only version:")
        for form, content in missing_content_pairs:
            print(f"  - {form} is missing {content}")
    else:
        print("✅ All form templates have corresponding content-only versions")
    
    # Check for orphaned content templates (without a full-page version)
    orphaned_content = []
    for content in content_templates:
        expected_form = content.replace("_content.html", ".html")
        if expected_form not in form_templates:
            orphaned_content.append((content, expected_form))
    
    if orphaned_content:
        print("\n⚠️ Content-only templates missing their full-page version:")
        for content, form in orphaned_content:
            print(f"  - {content} is missing {form}")
    else:
        print("✅ All content-only templates have corresponding full-page versions")
    
    # Check for possible templates in wrong locations
    misplaced_templates = []
    for path in existing:
        if path.endswith(".html"):
            if "templates/forms/" in path and ("outfit" in path.lower() or "component" in path.lower() or "vendor" in path.lower()):
                # This is correctly placed
                pass
            elif "templates/partials/" in path and any(x in path.lower() for x in ["card", "option", "list"]):
                # This is correctly placed
                pass
            elif "templates/outfits/" in path and "outfit" in path.lower():
                # This is correctly placed
                pass
            elif "templates/components/" in path and "component" in path.lower():
                # This is correctly placed
                pass
            else:
                # Check for possible misplacement
                if "outfit" in path.lower() and "templates/outfits/" not in path:
                    misplaced_templates.append((path, "templates/outfits/"))
                elif "component" in path.lower() and "templates/components/" not in path:
                    misplaced_templates.append((path, "templates/components/"))
                elif "form" in path.lower() and "templates/forms/" not in path:
                    misplaced_templates.append((path, "templates/forms/"))
                elif "partial" in path.lower() or "option" in path.lower() or "card" in path.lower():
                    if "templates/partials/" not in path:
                        misplaced_templates.append((path, "templates/partials/"))
    
    if misplaced_templates:
        print("\n⚠️ Possible misplaced templates:")
        for template, suggestion in misplaced_templates:
            print(f"  - {template} might belong in {suggestion}")
    else:
        print("✅ All templates appear to be in the correct directories")

if __name__ == "__main__":
    check_template_structure()