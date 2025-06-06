# File: utilities/setup_directories.py
# Revision: 1.0 - Create required directory structure for Outfit Manager

import os
from pathlib import Path

def create_directory_structure():
    """Create all required directories for the Outfit Manager project."""
    print("📁 CREATING DIRECTORY STRUCTURE")
    print("=" * 40)
    
    directories = [
        # Root directories
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
    
    created_dirs = []
    existing_dirs = []
    
    for directory in directories:
        dir_path = Path(directory)
        
        if dir_path.exists():
            existing_dirs.append(directory)
            print(f"✅ {directory} (already exists)")
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(directory)
                print(f"🆕 {directory} (created)")
            except Exception as e:
                print(f"❌ {directory} (failed: {e})")
    
    # Create __init__.py files for Python packages
    init_files = [
        "models/__init__.py",
        "routers/__init__.py", 
        "services/__init__.py",
        "utilities/__init__.py",
    ]
    
    created_init = []
    existing_init = []
    
    print(f"\n📄 CREATING __init__.py FILES")
    print("=" * 30)
    
    for init_file in init_files:
        init_path = Path(init_file)
        
        if init_path.exists():
            existing_init.append(init_file)
            print(f"✅ {init_file} (already exists)")
        else:
            try:
                with open(init_path, 'w', encoding='utf-8') as f:
                    f.write(f"# File: {init_file}\n")
                    f.write(f"# Revision: 1.0 - Package initialization\n")
                created_init.append(init_file)
                print(f"🆕 {init_file} (created)")
            except Exception as e:
                print(f"❌ {init_file} (failed: {e})")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 15)
    print(f"   📁 Directories:")
    print(f"      ✅ Existing: {len(existing_dirs)}")
    print(f"      🆕 Created: {len(created_dirs)}")
    print(f"   📄 __init__.py files:")
    print(f"      ✅ Existing: {len(existing_init)}")
    print(f"      🆕 Created: {len(created_init)}")
    
    total_created = len(created_dirs) + len(created_init)
    if total_created > 0:
        print(f"\n🎉 Successfully created {total_created} items!")
    else:
        print(f"\n✅ All directories and files already exist!")
    
    return True

def create_placeholder_files():
    """Create placeholder files for essential static assets."""
    print(f"\n📄 CREATING PLACEHOLDER FILES")
    print("=" * 30)
    
    placeholder_files = {
        "static/images/.gitkeep": "# Keep this directory in git",
        "templates/components/.gitkeep": "# Keep this directory in git", 
        "templates/outfits/.gitkeep": "# Keep this directory in git",
        "templates/vendors/.gitkeep": "# Keep this directory in git",
        "templates/pieces/.gitkeep": "# Keep this directory in git",
        "templates/forms/.gitkeep": "# Keep this directory in git",
        "templates/partials/.gitkeep": "# Keep this directory in git",
    }
    
    created_files = []
    existing_files = []
    
    for file_path, content in placeholder_files.items():
        path = Path(file_path)
        
        if path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path} (already exists)")
        else:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content + "\n")
                created_files.append(file_path)
                print(f"🆕 {file_path} (created)")
            except Exception as e:
                print(f"❌ {file_path} (failed: {e})")
    
    print(f"\n📊 Placeholder Files Summary:")
    print(f"   ✅ Existing: {len(existing_files)}")
    print(f"   🆕 Created: {len(created_files)}")
    
    return True

def verify_structure():
    """Verify the created directory structure."""
    print(f"\n🔍 VERIFYING STRUCTURE")
    print("=" * 25)
    
    required_dirs = [
        "models", "routers", "services", "utilities", "static",
        "static/css", "static/js", "static/images", "templates",
        "templates/components", "templates/outfits", 
        "templates/vendors", "templates/pieces",
        "templates/forms", "templates/partials"
    ]
    
    all_exist = True
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} (missing)")
            all_exist = False
    
    if all_exist:
        print(f"\n🎉 All required directories exist!")
        print(f"📋 Ready for file creation.")
    else:
        print(f"\n⚠️  Some directories are missing.")
        print(f"💡 Re-run this script to create them.")
    
    return all_exist

def run_setup():
    """Run the complete directory setup process."""
    print("🚀 OUTFIT MANAGER DIRECTORY SETUP")
    print("=" * 50)
    print(f"📁 Working directory: {os.getcwd()}")
    
    try:
        # Create directories
        create_directory_structure()
        
        # Create placeholder files
        create_placeholder_files()
        
        # Verify structure
        verify_structure()
        
        print(f"\n✅ SETUP COMPLETE!")
        print(f"🎯 Next steps:")
        print(f"   1. Create your Python files (main.py, models, routers, etc.)")
        print(f"   2. Create your template files")
        print(f"   3. Create your static files (CSS, JS)")
        print(f"   4. Run 'python debug.py' to validate")
        print(f"   5. Run 'uvicorn main:app --reload' to start")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_setup()
    
    if success:
        print(f"\n🎉 Directory setup completed successfully!")
    else:
        print(f"\n❌ Directory setup failed.")
    
    exit(0 if success else 1)