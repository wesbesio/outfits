# File: routers/vendors.py
# Revision: 1.0 - Complete vendor CRUD with HTML responses

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from typing import Optional, List

from models import Vendor, Component
from models.database import get_session
from services.template_service import templates

router = APIRouter()

# Helper function to convert HTML checkbox to boolean
def form_bool(value: Optional[str]) -> bool:
    """Convert HTML checkbox value to boolean."""
    return value is not None and value.lower() in ("true", "on", "1", "yes")

# --- HTML Page Endpoints ---

@router.get("/vendors/", response_class=HTMLResponse)
async def list_vendors_page(request: Request, session: Session = Depends(get_session)):
    """HTML page to list vendors. Returns full page or content block based on HX-Request."""
    context = {"request": request}

    if request.headers.get("hx-request"):
        return templates.TemplateResponse("vendors/list_main_content.html", context)
    
    return templates.TemplateResponse("vendors/list.html", context)

@router.get("/vendors/new", response_class=HTMLResponse)
async def create_vendor_page(request: Request):
    """HTML page to create a new vendor. Handles HX-Request for partial updates."""
    template_vars = {
        "request": request, 
        "vendor": None, 
        "edit_mode": True, 
        "form_action": "/api/vendors/"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("vendors/detail_main_content.html", template_vars)
    return templates.TemplateResponse("vendors/detail.html", template_vars)

@router.get("/vendors/{venid}", response_class=HTMLResponse)
async def get_vendor_page(venid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific vendor. Handles HX-Request for partial updates."""
    vendor = session.get(Vendor, venid)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")
    
    template_vars = {"request": request, "vendor": vendor, "edit_mode": False}
    
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("vendors/detail_main_content.html", template_vars)
    return templates.TemplateResponse("vendors/detail.html", template_vars)

@router.get("/vendors/{venid}/edit", response_class=HTMLResponse)
async def edit_vendor_page(venid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to edit a specific vendor. Handles HX-Request for partial updates."""
    vendor = session.get(Vendor, venid)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    template_vars = {
        "request": request, 
        "vendor": vendor, 
        "edit_mode": True, 
        "form_action": f"/api/vendors/{venid}"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("vendors/detail_main_content.html", template_vars)
    return templates.TemplateResponse("vendors/detail.html", template_vars)

# --- HTMX/API Endpoints (returning HTML fragments or JSON) ---

@router.get("/api/vendors/", response_class=HTMLResponse)
async def list_vendors_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc",
    show_inactive: Optional[str] = None
):
    """API endpoint to list vendors (HTMX fragment for the card grid)."""
    
    try:
        # Build query with proper error handling
        query = select(Vendor)
        
        # Apply active filter unless show_inactive is checked
        show_inactive_bool = form_bool(show_inactive)
        if not show_inactive_bool:
            query = query.where(Vendor.active == True)

        # Apply search filter if provided
        if q:
            query = query.where(Vendor.name.ilike(f"%{q}%") | Vendor.description.ilike(f"%{q}%"))

        # Handle sorting with fallback to name if invalid sort_by
        valid_sort_fields = ['name', 'description']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
            
        sort_field = getattr(Vendor, sort_by, Vendor.name)
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
            
        # Execute query with error handling
        vendors = session.exec(query).all()
        
        # Return template response
        return templates.TemplateResponse(
            "vendors/list_content.html", {"request": request, "vendors": vendors}
        )
        
    except Exception as e:
        # Proper error handling instead of letting exceptions bubble up
        print(f"Error in list_vendors_api: {e}")  # Log for debugging
        
        # Return user-friendly error message
        error_html = f"""
        <div id="vendor-list-container" class="card-grid">
            <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                <p>Sorry, there was an error loading vendors.</p>
                <p style="font-size: 0.9em;">Please try refreshing the page or contact support if the problem persists.</p>
            </div>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)

@router.post("/api/vendors/", response_class=HTMLResponse)
async def create_vendor(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    active: Optional[str] = Form(None)
):
    """API endpoint to create a new vendor."""
    # Convert HTML form data to proper types
    description = description.strip() or None
    active_bool = form_bool(active) if active is not None else True
    
    new_vendor = Vendor(
        name=name, 
        description=description,
        active=active_bool
    )
    session.add(new_vendor)
    session.commit()
    session.refresh(new_vendor)

    response = RedirectResponse(url=f"/vendors/{new_vendor.venid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/vendors/{new_vendor.venid}" 
    return response

@router.put("/api/vendors/{venid}", response_class=HTMLResponse)
async def update_vendor(
    venid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    active: Optional[str] = Form(None),
    flag: Optional[str] = Form(None)
):
    """API endpoint to update an existing vendor."""
    
    vendor = session.get(Vendor, venid)
    if not vendor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    # Convert HTML form data to proper types
    description = description.strip() or None
    active_bool = form_bool(active) if active is not None else vendor.active
    flag_bool = form_bool(flag)

    vendor.name = name
    vendor.description = description
    vendor.active = active_bool
    vendor.flag = flag_bool

    session.add(vendor)
    session.commit()
    session.refresh(vendor)

    response = RedirectResponse(url=f"/vendors/{vendor.venid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/vendors/{vendor.venid}"
    return response

@router.delete("/api/vendors/{venid}")
async def delete_vendor(venid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete a vendor."""
    vendor_to_delete = session.get(Vendor, venid)
    if not vendor_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found")

    # Check if vendor is used by any components
    linked_components = session.exec(select(Component).where(Component.vendorid == venid, Component.active == True)).all()
    
    if linked_components:
        # Don't delete if components are using this vendor
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot delete vendor. {len(linked_components)} active components are using this vendor."
        )

    vendor_to_delete.active = False
    session.add(vendor_to_delete)
    session.commit()

    response = HTMLResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = "/vendors/" 
    return response

@router.get("/api/vendors/{venid}/components", response_class=HTMLResponse)
async def get_components_by_vendor(venid: int, request: Request, session: Session = Depends(get_session)):
    """HTMX endpoint to list components using a specific vendor."""
    vendor = session.get(Vendor, venid)
    if not vendor:
        return HTMLResponse("<p class='text-center text-secondary'>Vendor not found.</p>")

    components = session.exec(
        select(Component)
        .where(Component.vendorid == venid, Component.active == True)
        .order_by(Component.name)
    ).all()

    if components:
        return templates.TemplateResponse(
            "components/list_content.html", 
            {"request": request, "components": components}
        )
    else:
        return HTMLResponse("<p class='text-center text-secondary'>No active components found from this vendor.</p>")