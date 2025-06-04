# File: utilities/debug_outfit_form.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import os
import sys
import traceback
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

def debug_outfit_templates():
    """Debug outfit template availability and structure."""
    # Change to parent directory for template operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("🔍 DEBUGGING OUTFIT FORM LOADING")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Check if template files exist
        template_files = [
            "templates/outfits/detail.html",
            "templates/outfits/detail_main_content.html", 
            "templates/forms/outfit_form_content.html",
            "templates/partials/component_checkboxes.html",
            "templates/outfits/detail_content.html",
            "templates/outfits/list.html",
            "templates/outfits/list_main_content.html",
            "templates/outfits/list_content.html",
            "templates/base.html"
        ]
        
        print("📂 Checking template files:")
        missing_templates = []
        for template_file in template_files:
            file_path = Path(template_file)
            if file_path.exists():
                print(f"   ✅ {template_file} exists")
                # Check file size
                size = file_path.stat().st_size
                print(f"      Size: {size} bytes")
            else:
                print(f"   ❌ {template_file} MISSING")
                missing_templates.append(template_file)
        
        if missing_templates:
            print(f"\n⚠️  Missing templates: {missing_templates}")
        
        # Test template rendering
        print(f"\n🧪 Testing template imports:")
        try:
            from services.template_service import templates
            print("   ✅ Template service imported successfully")
            
            # Test template loading
            try:
                # Try to get a template
                template = templates.get_template("base.html")
                print("   ✅ Base template loaded successfully")
            except Exception as e:
                print(f"   ❌ Template loading failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Template service import failed: {e}")
            return
        
        # Test model imports
        print(f"\n📦 Testing model imports:")
        try:
            from models import Outfit, Component, Out2Comp
            print("   ✅ Models imported successfully")
            
            # Check Outfit model structure
            print(f"   📋 Outfit model fields:")
            if hasattr(Outfit, '__annotations__'):
                annotations = Outfit.__annotations__
                print(f"      {list(annotations.keys())}")
                
                # Verify vendorid is removed
                if 'vendorid' not in annotations:
                    print(f"      ✅ vendorid successfully removed from Outfit model")
                else:
                    print(f"      ❌ vendorid still present in Outfit model")
                    
                # Verify score is present
                if 'score' in annotations:
                    print(f"      ✅ score successfully added to Outfit model")
                else:
                    print(f"      ❌ score missing from Outfit model")
            
        except Exception as e:
            print(f"   ❌ Model import failed: {e}")
            traceback.print_exc()
            return
        
        # Test database connection
        print(f"\n🗄️  Testing database connection:")
        try:
            from models.database import get_session, engine
            from sqlmodel import Session, select
            
            with Session(engine) as session:
                # Test querying components
                components = session.exec(select(Component).where(Component.active == True)).all()
                print(f"   ✅ Database connection successful")
                print(f"   📊 Found {len(components)} active components")
                
                # Test querying outfits
                outfits = session.exec(select(Outfit).where(Outfit.active == True)).all()
                print(f"   📊 Found {len(outfits)} active outfits")
                
                # Test outfit score field
                if outfits:
                    sample_outfit = outfits[0]
                    if hasattr(sample_outfit, 'score'):
                        print(f"   ✅ Score field accessible in outfit (value: {sample_outfit.score})")
                    else:
                        print(f"   ❌ Score field not accessible in outfit")
                
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            traceback.print_exc()
            return
        
        # Test route handling
        print(f"\n🛣️  Testing route setup:")
        try:
            from routers.outfits import router, get_outfit_form_context
            print("   ✅ Outfit router imported successfully")
            
            # Check if the routes are properly defined
            route_paths = [route.path for route in router.routes]
            print(f"   📍 Defined routes: {route_paths}")
            
            required_routes = ["/outfits/", "/outfits/new", "/outfits/{outid}", "/outfits/{outid}/edit"]
            for route in required_routes:
                if any(route in path for path in route_paths):
                    print(f"   ✅ {route} route found")
                else:
                    print(f"   ❌ {route} route MISSING")
            
            # Check for score endpoints
            score_routes = ["/api/outfits/{outid}/score/increment", "/api/outfits/{outid}/score/decrement"]
            for route in score_routes:
                if any(route in path for path in route_paths):
                    print(f"   ✅ {route} score route found")
                else:
                    print(f"   ❌ {route} score route MISSING")
                    
        except Exception as e:
            print(f"   ❌ Router import failed: {e}")
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_outfit_form_context():
    """Test the outfit form context function directly."""
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print(f"\n🧪 TESTING OUTFIT FORM CONTEXT")
        print("=" * 30)
        
        try:
            from fastapi import Request
            from models.database import get_session, engine
            from sqlmodel import Session
            from routers.outfits import get_outfit_form_context
            
            # Create a mock request
            class MockRequest:
                def __init__(self):
                    self.headers = {}
                    
            mock_request = MockRequest()
            
            with Session(engine) as session:
                # Test the context function
                import asyncio
                
                async def test_context():
                    try:
                        context = await get_outfit_form_context(mock_request, session)
                        print(f"   ✅ Form context generated successfully")
                        print(f"   📋 Context keys: {list(context.keys())}")
                        
                        if 'all_active_components' in context:
                            components = context['all_active_components']
                            print(f"   📊 Components in context: {len(components)}")
                            if components:
                                print(f"      Sample component: {components[0].name}")
                        
                        return context
                    except Exception as e:
                        print(f"   ❌ Form context generation failed: {e}")
                        traceback.print_exc()
                        return None
                
                context = asyncio.run(test_context())
                return context
                
        except Exception as e:
            print(f"   ❌ Context test setup failed: {e}")
            traceback.print_exc()
            return None
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_template_rendering():
    """Test template rendering with mock data."""
    # Change to parent directory for template operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print(f"\n🎨 TESTING TEMPLATE RENDERING")
        print("=" * 30)
        
        try:
            from services.template_service import templates
            from models import Outfit, Component
            
            # Create mock data
            mock_outfit = Outfit(
                outid=1,
                name="Test Outfit",
                description="Test Description",
                notes="Test Notes",
                totalcost=5000,
                score=3,
                active=True,
                flag=False
            )
            
            mock_component = Component(
                comid=1,
                name="Test Component",
                brand="Test Brand",
                cost=1000,
                description="Test Description",
                notes="Test Notes",
                vendorid=1,
                pieceid=1,
                active=True,
                flag=False
            )
            
            # Mock request
            class MockRequest:
                def __init__(self):
                    self.headers = {}
                    self.url = "http://localhost:8000/outfits/new"
                    self.method = "GET"
            
            mock_request = MockRequest()
            
            # Test outfit form template
            test_context = {
                'request': mock_request,
                'outfit': None,
                'edit_mode': True,
                'form_action': '/api/outfits/',
                'components': [mock_component],
                'current_component_ids': set(),
                'error': None,
                'associated_components': []
            }
            
            try:
                response = templates.TemplateResponse("outfits/detail_main_content.html", test_context)
                print(f"   ✅ Outfit form template rendered successfully")
            except Exception as e:
                print(f"   ❌ Outfit form template rendering failed: {e}")
                traceback.print_exc()
            
            # Test outfit detail template
            detail_context = {
                'request': mock_request,
                'outfit': mock_outfit,
                'edit_mode': False,
                'associated_components': [mock_component]
            }
            
            try:
                response = templates.TemplateResponse("outfits/detail_content.html", detail_context)
                print(f"   ✅ Outfit detail template rendered successfully")
            except Exception as e:
                print(f"   ❌ Outfit detail template rendering failed: {e}")
                traceback.print_exc()
                
        except Exception as e:
            print(f"   ❌ Template rendering test setup failed: {e}")
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def check_css_and_js():
    """Check static CSS and JS files."""
    # Change to parent directory for static file operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print(f"\n🎨 CHECKING STATIC FILES")
        print("=" * 30)
        
        static_files = [
            "static/css/main.css",
            "static/js/form-error-handler.js",
            "static/js/image-preview.js",
            "static/images/placeholder.svg"
        ]
        
        for static_file in static_files:
            file_path = Path(static_file)
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {static_file} exists ({size} bytes)")
                
                # Check for score-related styles in CSS
                if static_file.endswith("main.css"):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if '.score-display' in content:
                            print(f"      ✅ Score display styles found")
                        else:
                            print(f"      ❌ Score display styles missing")
                        if '.score-badge' in content:
                            print(f"      ✅ Score badge styles found")
                        else:
                            print(f"      ❌ Score badge styles missing")
            else:
                print(f"   ❌ {static_file} MISSING")
                
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    debug_outfit_templates()
    test_outfit_form_context()
    test_template_rendering()
    check_css_and_js()