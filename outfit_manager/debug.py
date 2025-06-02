# File: debug.py
# Revision: 3.5 - Add check for component detail content template

# Update the required_structure list in check_template_structure function:

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
    "templates/components/detail.html",       # Ensure this is checked
    
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




# Add to required_structure list:
    # Template files - Content-only templates for HTMX
    "templates/forms/outfit_form_content.html",      # 🆕 Content-only template
    "templates/forms/component_form_content.html",   # 🆕 Content-only template
    "templates/forms/vendor_form_content.html",      # 🆕 Content-only template
    "templates/outfits/list_content.html",           # 🆕 Content-only template
    "templates/components/list_content.html",        # 🆕 Content-only template
    "templates/components/detail_content.html",      # 🆕 Content-only template for component details
]