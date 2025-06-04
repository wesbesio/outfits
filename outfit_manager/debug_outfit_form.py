# File: debug_outfit_form.py
# Revision: 1.0 - Debug outfit form loading issues

import sys
import traceback
from pathlib import Path

def debug_outfit_templates():
    """Debug outfit template availability and structure."""
    print("🔍 DEBUGGING OUTFIT FORM LOADING")
    print("=" * 50)
    
    # Check if template files exist
    template_files = [
        "templates/outfits/detail.html",
        "templates/outfits/detail_main_content.html", 
        "templates/forms/outfit_form_content.html",
        "templates/partials/component_checkboxes.html"
    ]
    
    print("📂 Checking template files:")
    for template_file in template_files:
        file_path = Path(template_file)
        if file_path.exists():
            print(f"   ✅ {template_file} exists")
        else:
            print(f"   ❌ {template_file} MISSING")
    
    # Test template rendering
    print(f"\n🧪 Testing template imports:")
    try:
        from services.template_service import templates
        print("   ✅ Template service imported successfully")
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
                
    except Exception as e:
        print(f"   ❌ Router import failed: {e}")
        traceback.print_exc()

def test_outfit_form_context():
    """Test the outfit form context function directly."""
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

if __name__ == "__main__":
    debug_outfit_templates()
    test_outfit_form_context()