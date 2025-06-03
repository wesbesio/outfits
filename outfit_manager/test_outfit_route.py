# File: test_outfit_route.py
# Revision: 1.0 - Test the outfit new route directly

import asyncio
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

def test_outfit_new_route():
    """Test the /outfits/new route directly."""
    print("🧪 TESTING /outfits/new ROUTE")
    print("=" * 40)
    
    try:
        # Import the main app
        from main import app
        
        # Create test client
        client = TestClient(app)
        
        print("✅ App and client created successfully")
        
        # Test the route
        print("📡 Testing GET /outfits/new...")
        response = client.get("/outfits/new")
        
        print(f"   📊 Response status: {response.status_code}")
        print(f"   📋 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Route responded successfully")
            content = response.text
            print(f"   📄 Response length: {len(content)} characters")
            
            # Check if it contains form elements
            if "outfit-form-container" in content:
                print("   ✅ Form container found in response")
            else:
                print("   ❌ Form container NOT found in response")
                
            if "form" in content and "outfit" in content.lower():
                print("   ✅ Form elements found in response")
            else:
                print("   ❌ Form elements NOT found in response")
                
            # Check for errors in content
            if "error" in content.lower() or "exception" in content.lower():
                print("   ⚠️  Possible error in response content")
                # Print first 500 chars to see error
                print(f"   📄 Response snippet: {content[:500]}...")
                
        else:
            print(f"   ❌ Route failed with status {response.status_code}")
            print(f"   📄 Error response: {response.text[:500]}...")
            
        # Test HTMX request
        print("\n📡 Testing HTMX GET /outfits/new...")
        htmx_response = client.get("/outfits/new", headers={"hx-request": "true"})
        
        print(f"   📊 HTMX Response status: {htmx_response.status_code}")
        
        if htmx_response.status_code == 200:
            print("   ✅ HTMX route responded successfully")
            htmx_content = htmx_response.text
            print(f"   📄 HTMX Response length: {len(htmx_content)} characters")
        else:
            print(f"   ❌ HTMX route failed with status {htmx_response.status_code}")
            print(f"   📄 HTMX Error response: {htmx_response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Route test failed: {e}")
        import traceback
        traceback.print_exc()

def check_template_syntax():
    """Check template syntax for common issues."""
    print(f"\n🔍 CHECKING TEMPLATE SYNTAX")
    print("=" * 40)
    
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        
        # Create Jinja2 environment
        env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add the cents_to_dollars filter
        def cents_to_dollars_filter(cents):
            if cents is None:
                return "0.00"
            return f"{cents / 100:.2f}"
        
        env.filters['cents_to_dollars'] = cents_to_dollars_filter
        
        # Test template loading
        templates_to_test = [
            'outfits/detail.html',
            'outfits/detail_main_content.html',
            'forms/outfit_form_content.html'
        ]
        
        for template_name in templates_to_test:
            try:
                template = env.get_template(template_name)
                print(f"   ✅ {template_name} syntax OK")
                
                # Try a basic render with minimal context
                test_context = {
                    'request': None,
                    'outfit': None,
                    'edit_mode': True,
                    'form_action': '/api/outfits/',
                    'components': [],
                    'current_component_ids': set(),
                    'error': None,
                    'associated_components': []
                }
                
                try:
                    rendered = template.render(**test_context)
                    print(f"      ✅ {template_name} renders successfully")
                except Exception as render_error:
                    print(f"      ❌ {template_name} render failed: {render_error}")
                    
            except Exception as e:
                print(f"   ❌ {template_name} syntax error: {e}")
                
    except Exception as e:
        print(f"❌ Template syntax check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_outfit_new_route()
    check_template_syntax()