# File: utilities/live_debug.py
# Revision: 1.1 - Moved to utilities folder with updated imports

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from the main application
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_outfit_new_endpoint():
    """Create a debug version of the outfit new endpoint with extensive logging."""
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("🔧 CREATING DEBUG OUTFIT NEW ENDPOINT")
        print("=" * 50)
        print(f"📁 Working directory: {os.getcwd()}")
        
        try:
            from models.database import get_session
            from models import Component
            from services.template_service import templates
            from sqlmodel import select
            
            async def debug_create_outfit_page(request: Request, session: Session = Depends(get_session)):
                """Debug version of create_outfit_page with extensive logging."""
                
                logger.info(f"=== DEBUG CREATE OUTFIT PAGE CALLED ===")
                logger.info(f"Request URL: {request.url}")
                logger.info(f"Request method: {request.method}")
                logger.info(f"Request headers: {dict(request.headers)}")
                
                # Check if it's an HTMX request
                is_htmx = request.headers.get("hx-request")
                logger.info(f"Is HTMX request: {is_htmx}")
                
                try:
                    # Get all active components
                    logger.info("Fetching active components...")
                    all_active_components = session.exec(select(Component).where(Component.active == True).order_by(Component.name)).all()
                    logger.info(f"Found {len(all_active_components)} active components")
                    
                    if all_active_components:
                        logger.info(f"Sample component: {all_active_components[0].name}")
                    
                except Exception as e:
                    logger.error(f"Error fetching components: {e}")
                    all_active_components = []
                
                # Build template context
                template_vars = {
                    "request": request,
                    "components": all_active_components,
                    "outfit": None,
                    "edit_mode": True,
                    "form_action": "/api/outfits/",
                    "current_component_ids": set(),
                    "error": None,
                    "associated_components": []
                }
                
                logger.info(f"Template context keys: {list(template_vars.keys())}")
                logger.info(f"Components count in context: {len(template_vars['components'])}")
                logger.info(f"Edit mode: {template_vars['edit_mode']}")
                
                # Choose template based on request type
                if is_htmx:
                    template_name = "outfits/detail_main_content.html"
                    logger.info(f"Using HTMX template: {template_name}")
                else:
                    template_name = "outfits/detail.html"
                    logger.info(f"Using full page template: {template_name}")
                
                try:
                    logger.info(f"Attempting to render template: {template_name}")
                    response = templates.TemplateResponse(template_name, template_vars)
                    logger.info(f"Template rendered successfully")
                    return response
                    
                except Exception as e:
                    logger.error(f"Template rendering failed: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    
                    # Return a simple HTML response with error details
                    error_html = f"""
                    <div style="padding: 20px; background: #fee; border: 1px solid #f00; margin: 20px;">
                        <h3>Template Rendering Error</h3>
                        <p><strong>Template:</strong> {template_name}</p>
                        <p><strong>Error:</strong> {str(e)}</p>
                        <p><strong>Context keys:</strong> {list(template_vars.keys())}</p>
                        <pre>{traceback.format_exc()}</pre>
                    </div>
                    """
                    return HTMLResponse(content=error_html, status_code=500)
            
            return debug_create_outfit_page
            
        except Exception as e:
            logger.error(f"Failed to create debug endpoint: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_template_files():
    """Test if all required template files exist and are readable."""
    # Change to parent directory for template operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("\n📂 TESTING TEMPLATE FILES")
        print("=" * 30)
        print(f"📁 Working directory: {os.getcwd()}")
        
        required_templates = [
            "templates/outfits/detail.html",
            "templates/outfits/detail_main_content.html",
            "templates/forms/outfit_form_content.html",
            "templates/outfits/detail_content.html",
            "templates/base.html",
            "templates/partials/component_checkboxes.html",
            "templates/outfits/list.html",
            "templates/outfits/list_main_content.html",
            "templates/outfits/list_content.html"
        ]
        
        template_issues = []
        
        for template_path in required_templates:
            path = Path(template_path)
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"✅ {template_path} - {len(content)} chars")
                    
                    # Check for common issues
                    if "outfit" not in content.lower():
                        template_issues.append(f"⚠️  'outfit' not found in {template_path}")
                    if "form" not in content.lower() and "form" in template_path:
                        template_issues.append(f"⚠️  'form' not found in {template_path}")
                    if "score" not in content.lower() and "outfit" in template_path:
                        template_issues.append(f"⚠️  'score' not found in {template_path}")
                        
                    # Check for HTMX attributes
                    if "hx-" in content:
                        htmx_count = content.count("hx-")
                        print(f"      📊 {htmx_count} HTMX attributes found")
                    
                    # Check for score-related content
                    if "score" in content:
                        print(f"      ✅ Score-related content found")
                        
                except Exception as e:
                    template_issues.append(f"❌ {template_path} - Cannot read: {e}")
            else:
                template_issues.append(f"❌ {template_path} - MISSING")
        
        if template_issues:
            print(f"\n⚠️  Template Issues Found:")
            for issue in template_issues:
                print(f"   {issue}")
        else:
            print(f"\n✅ All templates look good!")
                
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def create_minimal_templates():
    """Create minimal working templates if they're missing."""
    # Change to parent directory for template operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("\n🛠️  CREATING MINIMAL TEMPLATES")
        print("=" * 30)
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Ensure directories exist
        Path("templates/outfits").mkdir(parents=True, exist_ok=True)
        Path("templates/forms").mkdir(parents=True, exist_ok=True)
        Path("templates/partials").mkdir(parents=True, exist_ok=True)
        
        # Minimal detail.html
        detail_html = """{% extends "base.html" %}
{% block content %}
{% include "outfits/detail_main_content.html" %}
{% endblock %}"""
        
        # Minimal detail_main_content.html with score support
        detail_main_content = """<div class="page-header">
    <h2>{% if edit_mode %}{% if outfit %}Edit Outfit{% else %}New Outfit{% endif %}{% else %}Outfit Details{% endif %}</h2>
    <div class="actions">
        {% if not edit_mode and outfit %}
            <a href="/outfits/{{ outfit.outid }}/edit" class="btn btn-outline">Edit</a>
        {% endif %}
        <a href="/outfits/" class="btn btn-secondary">Back to List</a>
    </div>
</div>

<div class="card">
    {% if edit_mode %}
        {% include "forms/outfit_form_content.html" %}
    {% else %}
        {% include "outfits/detail_content.html" %}
    {% endif %}
</div>"""
        
        # Minimal outfit_form_content.html with score field
        form_content = """<div id="outfit-form-container">
    <form hx-post="{{ form_action if form_action else '/api/outfits/' }}" 
          hx-target="#main-content" 
          hx-swap="innerHTML" 
          enctype="multipart/form-data">
        {% if error %}
            <div style="color: red; margin-bottom: 1rem;">{{ error }}</div>
        {% endif %}
        
        <div style="margin-bottom: 1rem;">
            <label for="name">Outfit Name:</label>
            <input type="text" id="name" name="name" 
                   value="{{ outfit.name if outfit else '' }}" 
                   required style="width: 100%; padding: 0.5rem;">
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label for="description">Description:</label>
            <textarea id="description" name="description" 
                      style="width: 100%; padding: 0.5rem;">{{ outfit.description if outfit else '' }}</textarea>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label for="score">Score:</label>
            <input type="number" id="score" name="score" 
                   value="{{ outfit.score if outfit else 0 }}" 
                   min="0" step="1" style="width: 200px; padding: 0.5rem;">
        </div>
        
        <div style="margin-bottom: 1rem;">
            <button type="submit" 
                    style="background: #8B5CF6; color: white; padding: 0.75rem 1.5rem; 
                           border: none; border-radius: 0.375rem; cursor: pointer;">
                {% if outfit and outfit.outid %}Update Outfit{% else %}Create Outfit{% endif %}
            </button>
            <a href="/outfits/" style="margin-left: 1rem;">Cancel</a>
        </div>
    </form>
</div>"""
        
        # Minimal detail_content.html with score display
        detail_content = """<div class="detail-container">
    {% if outfit %}
        <h3>{{ outfit.name }}</h3>
        <p><strong>Total Cost:</strong> ${{ (outfit.totalcost / 100)|round(2) }}</p>
        
        <!-- Score display with interactive buttons -->
        <div id="outfit-score-display" style="margin: 1rem 0; text-align: center;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; 
                        background: #F3E8FF; padding: 0.5rem; border-radius: 0.5rem;">
                <button hx-post="/api/outfits/{{ outfit.outid }}/score/decrement" 
                        hx-target="#outfit-score-display" 
                        hx-swap="outerHTML"
                        {% if outfit.score <= 0 %}disabled{% endif %}
                        style="width: 32px; height: 32px; border-radius: 50%; 
                               background: #EC4899; color: white; border: none; cursor: pointer;">
                    −
                </button>
                <span style="font-weight: bold; font-size: 1.1em; min-width: 2em; text-align: center;">
                    {{ outfit.score }}
                </span>
                <button hx-post="/api/outfits/{{ outfit.outid }}/score/increment" 
                        hx-target="#outfit-score-display" 
                        hx-swap="outerHTML"
                        style="width: 32px; height: 32px; border-radius: 50%; 
                               background: #8B5CF6; color: white; border: none; cursor: pointer;">
                    +
                </button>
            </div>
        </div>
        
        {% if outfit.description %}
            <p><strong>Description:</strong> {{ outfit.description }}</p>
        {% endif %}
        {% if outfit.notes %}
            <p><strong>Notes:</strong> {{ outfit.notes }}</p>
        {% endif %}
    {% else %}
        <p>Outfit not found.</p>
    {% endif %}
</div>"""
        
        # Minimal component checkboxes
        component_checkboxes = """<div style="border: 1px solid #ddd; padding: 1rem; border-radius: 0.5rem; max-height: 200px; overflow-y: auto;">
    {% if components %}
        {% for component in components %}
            <label style="display: block; margin-bottom: 0.5rem;">
                <input type="checkbox" name="component_ids" value="{{ component.comid }}"
                       {% if current_component_ids and component.comid in current_component_ids %}checked{% endif %}>
                {{ component.name }} 
                {% if component.brand %}({{ component.brand }}){% endif %}
                - ${{ (component.cost / 100)|round(2) }}
            </label>
        {% endfor %}
    {% else %}
        <p>No components available.</p>
    {% endif %}
</div>"""
        
        templates_to_create = [
            ("templates/outfits/detail.html", detail_html),
            ("templates/outfits/detail_main_content.html", detail_main_content),
            ("templates/forms/outfit_form_content.html", form_content),
            ("templates/outfits/detail_content.html", detail_content),
            ("templates/partials/component_checkboxes.html", component_checkboxes)
        ]
        
        created_count = 0
        for file_path, content in templates_to_create:
            path = Path(file_path)
            if not path.exists():
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Created {file_path}")
                    created_count += 1
                except Exception as e:
                    print(f"❌ Failed to create {file_path}: {e}")
            else:
                print(f"⏭️  {file_path} already exists")
        
        if created_count > 0:
            print(f"\n🎉 Created {created_count} minimal templates!")
        else:
            print(f"\n✅ All templates already exist")
                
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_jinja_template_syntax():
    """Test Jinja2 template syntax and rendering."""
    # Change to parent directory for template operations
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print("\n🎨 TESTING JINJA2 TEMPLATE SYNTAX")
        print("=" * 30)
        
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape
            
            # Create Jinja2 environment
            env = Environment(
                loader=FileSystemLoader('templates'),
                autoescape=select_autoescape(['html', 'xml'])
            )
            
            # Add filters
            def cents_to_dollars_filter(cents):
                if cents is None:
                    return "0.00"
                return f"{cents / 100:.2f}"
            
            env.filters['cents_to_dollars'] = cents_to_dollars_filter
            
            # Test templates
            templates_to_test = [
                'outfits/detail.html',
                'outfits/detail_main_content.html',
                'forms/outfit_form_content.html',
                'outfits/detail_content.html'
            ]
            
            for template_name in templates_to_test:
                try:
                    template = env.get_template(template_name)
                    print(f"   ✅ {template_name} syntax OK")
                    
                    # Try rendering with mock data
                    class MockOutfit:
                        def __init__(self):
                            self.outid = 1
                            self.name = "Test Outfit"
                            self.description = "Test Description"
                            self.notes = "Test Notes"
                            self.totalcost = 5000
                            self.score = 3
                            self.active = True
                            self.flag = False
                    
                    class MockRequest:
                        def __init__(self):
                            self.headers = {}
                            self.url = "http://localhost:8000/test"
                    
                    test_context = {
                        'request': MockRequest(),
                        'outfit': MockOutfit(),
                        'edit_mode': True,
                        'form_action': '/api/outfits/',
                        'components': [],
                        'current_component_ids': set(),
                        'error': None,
                        'associated_components': []
                    }
                    
                    try:
                        rendered = template.render(**test_context)
                        print(f"      ✅ {template_name} renders successfully ({len(rendered)} chars)")
                        
                        # Check for score-related content in rendered output
                        if 'score' in rendered:
                            print(f"      ✅ Score content found in rendered template")
                        
                    except Exception as render_error:
                        print(f"      ❌ {template_name} render failed: {render_error}")
                        
                except Exception as e:
                    print(f"   ❌ {template_name} syntax error: {e}")
                    
        except Exception as e:
            print(f"❌ Jinja2 template testing failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

def test_route_accessibility():
    """Test route accessibility and configuration."""
    # Change to parent directory for imports
    original_dir = os.getcwd()
    parent_dir = Path(__file__).parent.parent
    os.chdir(parent_dir)
    
    try:
        print(f"\n🛣️  TESTING ROUTE ACCESSIBILITY")
        print("=" * 30)
        
        try:
            from fastapi.testclient import TestClient
            from main import app
            
            client = TestClient(app)
            
            # Test key routes
            routes_to_test = [
                ('/outfits/', 'GET', 'Outfits list'),
                ('/outfits/new', 'GET', 'New outfit form'),
                ('/components/', 'GET', 'Components list'),
                ('/components/new', 'GET', 'New component form')
            ]
            
            for route, method, description in routes_to_test:
                try:
                    if method == 'GET':
                        response = client.get(route)
                    
                    print(f"   {description} ({method} {route}): {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text
                        # Check for key elements
                        if 'outfit' in content.lower() or 'component' in content.lower():
                            print(f"      ✅ Contains expected content")
                        if 'score' in content.lower() and 'outfit' in route:
                            print(f"      ✅ Contains score-related content")
                    else:
                        print(f"      ❌ Unexpected status code")
                        
                except Exception as e:
                    print(f"   ❌ {description}: {e}")
            
            # Test HTMX routes
            print(f"\n📡 Testing HTMX routes:")
            htmx_routes = [
                ('/outfits/new', 'New outfit HTMX'),
                ('/components/new', 'New component HTMX')
            ]
            
            for route, description in htmx_routes:
                try:
                    response = client.get(route, headers={"hx-request": "true"})
                    print(f"   {description}: {response.status_code}")
                    
                    if response.status_code == 200:
                        content = response.text
                        if len(content) > 0:
                            print(f"      ✅ HTMX response received ({len(content)} chars)")
                        else:
                            print(f"      ❌ Empty HTMX response")
                    
                except Exception as e:
                    print(f"   ❌ {description}: {e}")
                    
        except Exception as e:
            print(f"❌ Route testing failed: {e}")
            import traceback
            traceback.print_exc()
            
    finally:
        # Change back to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    test_template_files()
    create_minimal_templates()
    test_jinja_template_syntax()
    test_route_accessibility()
    
    debug_endpoint = debug_outfit_new_endpoint()
    if debug_endpoint:
        print(f"\n🎯 Debug endpoint created successfully")
        print(f"   You can now test the outfit form with detailed logging")
    else:
        print(f"\n❌ Failed to create debug endpoint")