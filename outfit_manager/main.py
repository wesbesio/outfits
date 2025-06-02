# File: main.py
# Revision: 3.5 - Add direct endpoint for component outfits

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn
import traceback

from models.database import create_db_and_tables, get_session
from sqlmodel import Session, select
from models import Outfit, Component, Vendor, Piece, ComponentResponse
from services.seed_data import create_seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    # Create seed data
    session = next(get_session())
    create_seed_data(session)
    session.close()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Outfit Manager",
    description="Fashion outfit and component management system with HTMX frontend",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates - define right in main.py
templates = Jinja2Templates(directory="templates")

# Import only the API routers (no web_routes)
from routers import outfits, components, vendors, images, pieces

# Include API routers with explicit prefixes
app.include_router(outfits.router, prefix="/api/outfits", tags=["outfits"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(pieces.router, prefix="/api/pieces", tags=["pieces"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

# HOME PAGE
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# OUTFITS LIST
@app.get("/outfits", response_class=HTMLResponse)
async def outfits_list(request: Request):
    # Check if this is an HTMX request
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "outfits/list_content.html" if is_htmx else "outfits/list.html"
    
    # Add debug info to help identify issues
    print(f"Serving outfits list with template: {template}, HTMX request: {is_htmx}")
    
    return templates.TemplateResponse(template, {"request": request})

# COMPONENTS LIST
@app.get("/components", response_class=HTMLResponse)
async def components_list(request: Request):
    # Check if this is an HTMX request
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "components/list_content.html" if is_htmx else "components/list.html"
    
    # Add debug info
    print(f"Serving components list with template: {template}, HTMX request: {is_htmx}")
    
    return templates.TemplateResponse(template, {"request": request})

# NEW COMPONENT FORM - Explicitly defined with alternate path
@app.get("/new-component", response_class=HTMLResponse)
async def new_component_form_alt(request: Request, session: Session = Depends(get_session)):
    """Alternative path for new component form"""
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        pieces = session.exec(select(Piece).where(Piece.active == True)).all()
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        template = "forms/component_form_content.html" if is_htmx else "forms/component_form.html"
        
        return templates.TemplateResponse(template, {
            "request": request,
            "component": None,
            "vendors": vendors,
            "pieces": pieces,
            "is_edit": False,
            "page_title": "Create New Component"
        })
    except Exception as e:
        error_msg = f"Error in new_component_form_alt: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return HTMLResponse(f"""
        <html>
            <body>
                <h1>Error Loading Component Form</h1>
                <p>{error_msg}</p>
                <pre>{traceback.format_exc()}</pre>
            </body>
        </html>
        """)

# Redirect /components/new to /new-component
@app.get("/components/new")
async def components_new_redirect():
    return RedirectResponse("/new-component", status_code=302)

# NEW OUTFIT FORM 
@app.get("/outfits/new", response_class=HTMLResponse)
async def new_outfit_form(request: Request, session: Session = Depends(get_session)):
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        template = "forms/outfit_form_content.html" if is_htmx else "forms/outfit_form.html"
        
        return templates.TemplateResponse(template, {
            "request": request,
            "outfit": None,
            "vendors": vendors,
            "is_edit": False,
            "page_title": "Create New Outfit"
        })
    except Exception as e:
        error_msg = f"Error in new_outfit_form: {str(e)}"
        print(error_msg)
        return HTMLResponse(f"<html><body><h1>Error</h1><p>{error_msg}</p></body></html>")

# NEW VENDOR FORM
@app.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor_form(request: Request):
    try:
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        template = "forms/vendor_form_content.html" if is_htmx else "forms/vendor_form.html"
        
        return templates.TemplateResponse(template, {
            "request": request,
            "vendor": None,
            "is_edit": False,
            "page_title": "Create New Vendor"
        })
    except Exception as e:
        error_msg = f"Error in new_vendor_form: {str(e)}"
        print(error_msg)
        return HTMLResponse(f"<html><body><h1>Error</h1><p>{error_msg}</p></body></html>")

# Debugging route
@app.get("/debug/routes", response_class=HTMLResponse)
async def debug_routes(request: Request):
    """Debug route to show all registered routes"""
    route_list = []
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = ",".join(route.methods) if hasattr(route, 'methods') and route.methods else "GET"
            route_list.append(f"<li>{route.path} [{methods}]</li>")
    
    return f"""
    <html>
        <head><title>Route Debugging</title></head>
        <body>
            <h1>Registered Routes</h1>
            <ul>{"".join(route_list)}</ul>
        </body>
    </html>
    """

# File: main.py
# Revision: 3.4 - Fix component detail route to handle HTMX requests

@app.get("/components/{component_id}", response_class=HTMLResponse)
async def component_detail(request: Request, component_id: int, session: Session = Depends(get_session)):
    """Render the component detail page"""
    try:
        # Get component by ID
        component = session.get(Component, component_id)
        
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Create component response with additional data
        component_response = ComponentResponse(
            **component.model_dump(),
            has_image=component.image is not None,
            vendor_name=component.vendor.name if component.vendor else None,
            piece_name=component.piece.name if component.piece else None
        )
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request') == 'true'
        template = "components/detail_content.html" if is_htmx else "components/detail.html"
        
        # For debugging
        print(f"Serving component detail for component_id: {component_id}, is_htmx: {is_htmx}, template: {template}")
        
        return templates.TemplateResponse(template, {
            "request": request,
            "component": component_response
        })
    except Exception as e:
        error_msg = f"Error in component_detail: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return HTMLResponse(f"""
        <html>
            <body>
                <h1>Error Loading Component Detail</h1>
                <p>{error_msg}</p>
                <pre>{traceback.format_exc()}</pre>
            </body>
        </html>
        """)


# Add this route directly in main.py, not in the router:
@app.get("/api/components/{component_id}/outfits", response_class=HTMLResponse)
async def component_outfits(request: Request, component_id: int, session: Session = Depends(get_session)):
    """Simple endpoint for component outfits - for debugging"""
    try:
        print(f"DEBUG: Direct outfits endpoint called for component ID: {component_id}")
        
        # Just return a static message for now to verify the route works
        return HTMLResponse("""
        <div style="padding: 20px; background: #f0f0f0; border-radius: 8px; text-align: center;">
            <h3>Outfits Debug View</h3>
            <p>This is a simplified endpoint for debugging.</p>
        </div>
        """)
    except Exception as e:
        print(f"ERROR in direct component_outfits: {str(e)}")
        traceback.print_exc()  # This will print the error in server logs
        
        # Return a simple error message
        return HTMLResponse("""
        <div style="padding: 20px; background: #ffeeee; border: 1px solid #ffaaaa; border-radius: 8px; text-align: center; color: #cc0000;">
            <h3>Error Loading Outfits</h3>
            <p>Check server logs for details.</p>
        </div>
        """)

        
# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)