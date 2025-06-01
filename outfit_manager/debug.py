# File: debug.py
# Revision: 3.1 - Updated for HTMX content-only templates and direct route handling
# Updated: Check for new content-only templates and removed loading indicator

import os

def check_template_structure():
    """Check if all required files exist and identify legacy files to remove"""
    base_dir = "."
    
    # Updated required structure after HTMX content-only templates implementation
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
        missing_templates = [item for item in missing if 'templates/' in item and 'forms/' not in item and not item.endswith('/') and '_content.html' not in item]
        missing_static = [item for item in missing if 'static/' in item and not item.endswith('/')]
        missing_routers = [item for item in missing if 'routers/' in item and item.endswith('.py')]
        missing_python = [item for item in missing if item.endswith('.py') and 'routers/' not in item and 'templates/' not in item]
        missing_other = [item for item in missing if item not in missing_dirs + missing_forms + missing_content_templates + missing_templates + missing_static + missing_routers + missing_python]
        
        if missing_dirs:
            print("\n📁 Missing Directories:")
            for item in missing_dirs:
                print(f"   - {item}")
                
        if missing_forms:
            print("\n📝 Missing Form Templates (CRITICAL):")
            for item in missing_forms:
                print(f"   - {item} 🚨")
                
        if missing_content_templates:
            print("\n📄 Missing Content-only Templates (CRITICAL for HTMX):")
            for item in missing_content_templates:
                print(f"   - {item} 🚨")
                
        if missing_templates:
            print("\n📄 Missing Templates:")
            for item in missing_templates:
                print(f"   - {item}")
                
        if missing_static:
            print("\n🎨 Missing Static Files:")
            for item in missing_static:
                print(f"   - {item}")
                
        if missing_routers:
            print("\n🔌 Missing Router Files:")
            for item in missing_routers:
                print(f"   - {item}")
                
        if missing_python:
            print("\n🐍 Missing Python Files:")
            for item in missing_python:
                print(f"   - {item}")
                
        if missing_other:
            print("\n📋 Missing Other Files:")
            for item in missing_other:
                print(f"   - {item}")
    
    # Show legacy files to remove
    if legacy_present:
        print("\n🗑️  LEGACY FILES TO REMOVE:")
        print("These files are no longer needed with the HTMX content-only templates and direct route handling:")
        for item in legacy_present:
            print(f"   - {item} ❌")
        
        print("\n🔧 Removal Commands:")
        for item in legacy_present:
            print(f"rm {item}")
    
    # Show fix commands for missing files
    if missing:
        print("\n🔧 Quick Fix Commands:")
        
        # Create missing directories
        missing_dirs = [d.rstrip('/') for d in missing if d.endswith('/')]
        if missing_dirs:
            print("# Create missing directories:")
            dirs_to_create = " ".join(missing_dirs)
            print(f"mkdir -p {dirs_to_create}")
        
        # Create missing files
        missing_files = [f for f in missing if not f.endswith('/')]
        if missing_files:
            print("\n# Create missing files:")
            for file in missing_files:
                print(f"touch {file}")
    
    if not missing and not legacy_present:
        print("🎉 PERFECT! All files are in the correct state!")
        print("✅ All required files exist")
        print("✅ No legacy files found")
        print("🚀 Your refactor is complete!")
    
    return missing, legacy_present

def check_file_sizes():
    """Check if important files have content (not empty)"""
    print("\n" + "="*60)
    print("📏 FILE SIZE CHECK:")
    
    critical_files = [
        # Form templates (most important)
        "templates/forms/outfit_form.html",
        "templates/forms/component_form.html", 
        "templates/forms/vendor_form.html",
        
        # Content-only templates (critical for HTMX)
        "templates/forms/outfit_form_content.html",
        "templates/forms/component_form_content.html",
        "templates/forms/vendor_form_content.html",
        "templates/outfits/list_content.html",
        "templates/components/list_content.html",
        
        # Updated templates
        "templates/base.html",
        "templates/outfits/list.html",
        "templates/components/list.html",
        
        # Updated static files
        "static/css/main.css",
        "static/js/main.js",
        
        # Updated routers
        "routers/outfits.py",
        "routers/components.py",
        "routers/vendors.py",
        "routers/__init__.py",  # Should not import web_routes
        
        # Core files - main.py is now critical with direct route handling
        "main.py",
        "models/__init__.py",
        "services/seed_data.py"
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            if size == 0:
                print(f"🚨 {file} - EMPTY (0 bytes) - CRITICAL!")
            elif size < 100:
                print(f"⚠️  {file} - Very small ({size} bytes)")
            elif size < 500:
                print(f"⚡ {file} - Small ({size} bytes)")
            else:
                print(f"✅ {file} - Good ({size} bytes)")
        else:
            print(f"❌ {file} - MISSING")
    
    # Special check for base.html (should not have loading indicator)
    if os.path.exists("templates/base.html"):
        try:
            with open("templates/base.html", "r") as f:
                content = f.read()
                if "loading-indicator" not in content:
                    print(f"✅ base.html does not contain loading indicator (good)")
                else:
                    print(f"🚨 base.html still contains loading indicator - should be removed!")
        except Exception as e:
            print(f"⚠️ Could not read base.html: {str(e)}")
    
    # Special check for main.py
    if os.path.exists("main.py"):
        try:
            with open("main.py", "r") as f:
                content = f.read()
                issues = []
                
                if "web_routes" in content:
                    issues.append("still imports web_routes (should be removed)")
                
                if "'HX-Request'" not in content and "\"HX-Request\"" not in content:
                    issues.append("may not detect HTMX requests properly")
                
                if "_content.html" not in content:
                    issues.append("may not serve content-only templates for HTMX requests")
                
                if issues:
                    print(f"🚨 main.py has issues: {', '.join(issues)}")
                else:
                    print(f"✅ main.py contains the required HTMX detection and content-only templates")
        except Exception as e:
            print(f"⚠️ Could not read main.py: {str(e)}")
    
    # Special check for routers/__init__.py
    if os.path.exists("routers/__init__.py"):
        try:
            with open("routers/__init__.py", "r") as f:
                content = f.read()
                if "web_routes" not in content:
                    print(f"✅ routers/__init__.py no longer imports web_routes (good)")
                else:
                    print(f"🚨 routers/__init__.py still imports web_routes - should be removed!")
        except Exception as e:
            print(f"⚠️ Could not read routers/__init__.py: {str(e)}")

def check_refactor_status():
    """Check if refactor has been properly implemented"""
    print("\n" + "="*60)
    print("🔄 HTMX CONTENT-ONLY TEMPLATES REFACTOR STATUS CHECK:")
    
    # Files that must be updated for refactor
    updated_files = {
        "templates/base.html": "Removed loading indicator",
        "static/css/main.css": "Removed loading indicator styles", 
        "static/js/main.js": "Removed loading functions",
        "main.py": "HTMX detection and content-only templates",
        "routers/__init__.py": "Removed web_routes import",
    }
    
    # New files that must exist
    new_files = {
        "templates/forms/outfit_form_content.html": "Content-only outfit form template",
        "templates/forms/component_form_content.html": "Content-only component form template",
        "templates/forms/vendor_form_content.html": "Content-only vendor form template",
        "templates/outfits/list_content.html": "Content-only outfits list template",
        "templates/components/list_content.html": "Content-only components list template",
    }
    
    # Legacy files that must be removed
    legacy_files = {
        "templates/partials/outfit_form.html": "Old modal form",
        "templates/partials/component_form.html": "Old modal form",
        "templates/partials/vendor_form.html": "Old modal form",
        "templates/partials/add_component_form.html": "Old modal form",
        "routers/web_routes.py": "Routes moved to main.py",
    }
    
    refactor_score = 0
    total_checks = len(updated_files) + len(new_files) + len(legacy_files)
    
    print("\n✅ Updated Files:")
    for file, description in updated_files.items():
        if os.path.exists(file) and os.path.getsize(file) > 0:
            # Special check for main.py
            if file == "main.py":
                try:
                    with open(file, "r") as f:
                        content = f.read()
                        if "'HX-Request'" in content or "\"HX-Request\"" in content:
                            print(f"   ✅ {file} - {description} (UPDATED)")
                            refactor_score += 1
                        else:
                            print(f"   ❌ {file} - {description} (NOT UPDATED)")
                except:
                    print(f"   ❓ {file} - {description} (COULD NOT READ)")
            # Special check for base.html
            elif file == "templates/base.html":
                try:
                    with open(file, "r") as f:
                        content = f.read()
                        if "loading-indicator" not in content:
                            print(f"   ✅ {file} - {description} (UPDATED)")
                            refactor_score += 1
                        else:
                            print(f"   ❌ {file} - {description} (NOT UPDATED)")
                except:
                    print(f"   ❓ {file} - {description} (COULD NOT READ)")
            # Special check for routers/__init__.py
            elif file == "routers/__init__.py":
                try:
                    with open(file, "r") as f:
                        content = f.read()
                        if "web_routes" not in content:
                            print(f"   ✅ {file} - {description} (UPDATED)")
                            refactor_score += 1
                        else:
                            print(f"   ❌ {file} - {description} (NOT UPDATED)")
                except:
                    print(f"   ❓ {file} - {description} (COULD NOT READ)")
            else:
                print(f"   ✅ {file} - {description}")
                refactor_score += 1
        else:
            print(f"   ❌ {file} - {description} (MISSING OR EMPTY)")
    
    print("\n🆕 New Files:")
    for file, description in new_files.items():
        if os.path.exists(file):
            if os.path.getsize(file) > 0:
                print(f"   ✅ {file} - {description}")
                refactor_score += 1
            else:
                print(f"   ⚠️  {file} - {description} (EMPTY)")
        else:
            print(f"   ❌ {file} - {description} (MISSING)")
    
    print("\n🗑️  Legacy Files (should be removed):")
    for file, description in legacy_files.items():
        if not os.path.exists(file):
            print(f"   ✅ {file} - {description} (REMOVED)")
            refactor_score += 1
        else:
            print(f"   ❌ {file} - {description} (STILL EXISTS)")
    
    completion_percent = (refactor_score / total_checks) * 100
    
    print(f"\n🎯 REFACTOR COMPLETION: {completion_percent:.0f}%")
    
    if completion_percent == 100:
        print("🎉 HTMX CONTENT-ONLY TEMPLATES REFACTOR COMPLETE!")
        print("🚀 Your app is ready to run!")
    elif completion_percent >= 80:
        print("⚡ Almost complete! Fix the remaining issues.")
    elif completion_percent >= 50:
        print("⚠️  Refactor in progress. Keep working on it.")
    else:
        print("🚨 Refactor not started or major issues found.")

if __name__ == "__main__":
    print("🔍 OUTFIT MANAGER - COMPREHENSIVE FILE CHECK")
    print("Checking file structure after HTMX content-only templates refactor...")
    print()
    
    missing, legacy_present = check_template_structure()
    check_file_sizes()
    check_refactor_status()
    
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    if not missing and not legacy_present:
        print("✅ Perfect! Your refactor is complete and ready to deploy!")
    else:
        if missing:
            print(f"❌ {len(missing)} required files missing")
        if legacy_present:
            print(f"🗑️  {len(legacy_present)} legacy files need removal")
        print("🔧 Follow the fix commands above to complete the refactor")
    
    print("\n🚀 Next step: Run 'python main.py' to test your application!")