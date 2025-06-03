# File: services/template_service.py
# Revision: 1.0 - Shared template service with custom filters

from fastapi.templating import Jinja2Templates

def cents_to_dollars_filter(cents: int) -> str:
    """Template filter to convert cents to dollar string."""
    if cents is None:
        return "0.00"
    return f"{cents / 100:.2f}"

def create_templates() -> Jinja2Templates:
    """Create a Jinja2Templates instance with custom filters."""
    templates = Jinja2Templates(directory="templates")
    templates.env.filters['cents_to_dollars'] = cents_to_dollars_filter
    return templates

# Shared templates instance
templates = create_templates()