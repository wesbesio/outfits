# File: live_debug.py
# Revision: 1.0 - Live debugging of outfit form loading with detailed logging

import logging
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_outfit_new_endpoint():
    """Create a debug version of the outfit new endpoint with extensive logging."""
    
    print("🔧 CREATING DEBUG OUTFIT NEW ENDPOINT")
    print("=" * 50)
    
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

def test_template_files():
    """Test if all required template files exist and are readable."""
    
    print("\n📂 TESTING TEMPLATE FILES")
    print("=" * 30)
    
    import os
    from pathlib import Path
    
    required_templates = [
        "templates/outfits/detail.html",
        "templates/outfits/detail_main_content.html",
        "templates/forms/outfit_form_content.html",
        "templates/base.html"
    ]
    
    for template_path in required_templates:
        path = Path(template_path)
        if path.exists():
            try:
                with open(path, 'r') as f:
                    content = f.read()
                print(f"✅ {template_path} - {len(content)} chars")
                
                # Check for common issues
                if "outfit" not in content.lower():
                    print(f"   ⚠️  Warning: 'outfit' not found in {template_path}")
                if "form" not in content.lower() and "form" in template_path:
                    print(f"   ⚠️  Warning: 'form' not found in {template_path}")
                    
            except Exception as e:
                print(f"❌ {template_path} - Cannot read: {e}")
        else:
            print(f"❌ {template_path} - MISSING")

def create_minimal_templates():
    """Create minimal working templates if they're missing."""
    
    print("\n🛠️  CREATING MINIMAL TEMPLATES")
    print("=" * 30)
    
    from pathlib import Path
    
    # Ensure directories exist
    Path("templates/outfits").mkdir(parents=True, exist_ok=True)
    Path("templates/forms").mkdir(parents=True, exist_ok=True)
    
    # Minimal detail.html
    detail_html = """{% extends "base.html" %}
{% block content %}
{% include "outfits/detail_main_content.html" %}
{% endblock %}"""
    
    # Minimal detail_main_content.html
    detail_main_content = """<div class="page-header">
    <h2>{% if edit_mode %}{% if outfit %}Edit Outfit{% else %}New Outfit{% endif %}{% else %}Outfit Details{% endif %}</h2>
    <div class="actions">
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
    
    # Minimal outfit_form_content.html
    form_content = """<div id="outfit-form-container">
    <form hx-post="{{ form_action if form_action else '/api/outfits/' }}" hx-target="#main-content" hx-swap="innerHTML" enctype="multipart/form-data">
        {% if error %}
            <div style="color: red; margin-bottom: 1rem;">{{ error }}</div>
        {% endif %}
        
        <div style="margin-bottom: 1rem;">
            <label for="name">Outfit Name:</label>
            <input type="text" id="name" name="name" value="{{ outfit.name if outfit else '' }}" required style="width: 100%; padding: 0.5rem;">
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label for="description">Description:</label>
            <textarea id="description" name="description" style="width: 100%; padding: 0.5rem;">{{ outfit.description if outfit else '' }}</textarea>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <button type="submit" style="background: #8B5CF6; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 0.375rem; cursor: pointer;">
                {% if outfit and outfit.outid %}Update Outfit{% else %}Create Outfit{% endif %}
            </button>
            <a href="/outfits/" style="margin-left: 1rem;">Cancel</a>
        </div>
    </form>
</div>"""
    
    templates_to_create = [
        ("templates/outfits/detail.html", detail_html),
        ("templates/outfits/detail_main_content.html", detail_main_content),
        ("templates/forms/outfit_form_content.html", form_content)
    ]
    
    for file_path, content in templates_to_create:
        path = Path(file_path)
        if not path.exists():
            try:
                with open(path, 'w') as f:
                    f.write(content)
                print(f"✅ Created {file_path}")
            except Exception as e:
                print(f"❌ Failed to create {file_path}: {e}")
        else:
            print(f"⏭️  {file_path} already exists")

if __name__ == "__main__":
    test_template_files()
    create_minimal_templates()
    
    debug_endpoint = debug_outfit_new_endpoint()
    if debug_endpoint:
        print(f"\n🎯 Debug endpoint created successfully")
        print(f"   You can now test the outfit form with detailed logging")
    else:
        print(f"\n❌ Failed to create debug endpoint")