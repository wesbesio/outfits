# File: routers/components.py
# Revision: 1.5 - Fixed search parameter handling and added error handling for better UX

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from typing import Optional, List, Union

from models import Component, Vendor, Piece, Outfit, Out2Comp
from models.database import get_session
from services.image_service import ImageService
from services.template_service import templates

router = APIRouter()

# Helper function to convert dollars to cents for storage
def dollars_to_cents(dollars: float) -> int:
    """Convert dollars to cents for database storage."""
    return int(round(dollars * 100))

# Helper function to convert HTML form string to Optional[int]
def form_int_or_none(value: str) -> Optional[int]:
    """Convert HTML form string to int or None."""
    if not value or not value.strip():
        return None
    try:
        return int(value)
    except ValueError:
        return None

# Helper function to convert HTML checkbox to boolean
def form_bool(value: Optional[str]) -> bool:
    """Convert HTML checkbox value to boolean."""
    return value is not None and value.lower() in ("true", "on", "1", "yes")

# NEW: Safe parameter conversion for search filters
def safe_int_conversion(value: Optional[str]) -> Optional[int]:
    """Safely convert string to int, returning None for empty/invalid values."""
    if not value or not value.strip():
        return None
    try:
        return int(value)
    except ValueError:
        return None

# Dependency for common template context (used for forms and potentially detail views)
async def get_form_template_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    return {"request": request, "vendors": vendors, "pieces": pieces}

# --- HTML Page Endpoints ---

@router.get("/components/", response_class=HTMLResponse)
async def list_components_page(request: Request, session: Session = Depends(get_session)):
    """HTML page to list components. Returns full page or content block based on HX-Request."""
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    context = {"request": request, "vendors": vendors, "pieces": pieces}

    if request.headers.get("hx-request"):
        return templates.TemplateResponse("components/list_main_content.html", context)
    
    return templates.TemplateResponse("components/list.html", context)

@router.get("/components/new", response_class=HTMLResponse)
async def create_component_page(request: Request, context: dict = Depends(get_form_template_context)):
    """HTML page to create a new component. Handles HX-Request for partial updates."""
    template_vars = {
        **context, 
        "component": None, 
        "edit_mode": True, 
        "form_action": "/api/components/"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("components/detail_main_content.html", template_vars)
    return templates.TemplateResponse("components/detail.html", template_vars)

@router.get("/components/{comid}", response_class=HTMLResponse)
async def get_component_page(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific component. Handles HX-Request for partial updates."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    
    template_vars = {"request": request, "component": component, "edit_mode": False}
    
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("components/detail_main_content.html", template_vars)
    return templates.TemplateResponse("components/detail.html", template_vars)

@router.get("/components/{comid}/edit", response_class=HTMLResponse)
async def edit_component_page(comid: int, request: Request, context: dict = Depends(get_form_template_context), session: Session = Depends(get_session)):
    """HTML page to edit a specific component. Handles HX-Request for partial updates."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    template_vars = {
        **context, 
        "component": component, 
        "edit_mode": True, 
        "form_action": f"/api/components/{comid}"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("components/detail_main_content.html", template_vars)
    return templates.TemplateResponse("components/detail.html", template_vars)


# --- HTMX/API Endpoints (returning HTML fragments or JSON) ---

@router.get("/api/components/", response_class=HTMLResponse)
async def list_components_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    vendorid: Optional[str] = None,  # FIXED: Changed from Optional[int] to Optional[str]
    pieceid: Optional[str] = None,   # FIXED: Changed from Optional[int] to Optional[str]
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    """API endpoint to list components (HTMX fragment for the card grid). FIXED: Proper parameter handling."""
    
    try:
        # FIXED: Safely convert string parameters to integers
        vendorid_int = safe_int_conversion(vendorid)
        pieceid_int = safe_int_conversion(pieceid)
        
        # Build query with proper error handling
        query = select(Component).where(Component.active == True)

        # Apply filters with converted parameters
        if q:
            query = query.where(Component.name.ilike(f"%{q}%") | Component.description.ilike(f"%{q}%") | Component.brand.ilike(f"%{q}%"))
        if vendorid_int:
            query = query.where(Component.vendorid == vendorid_int)
        if pieceid_int:
            query = query.where(Component.pieceid == pieceid_int)

        # Handle sorting with fallback to name if invalid sort_by
        valid_sort_fields = ['name', 'cost', 'brand']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
            
        sort_field = getattr(Component, sort_by, Component.name)
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
            
        # Execute query with error handling
        components = session.exec(query).all()
        
        # Return template response
        return templates.TemplateResponse(
            "components/list_content.html", {"request": request, "components": components}
        )
        
    except Exception as e:
        # FIXED: Proper error handling instead of letting exceptions bubble up
        print(f"Error in list_components_api: {e}")  # Log for debugging
        
        # Return user-friendly error message
        error_html = f"""
        <div id="component-list-container" class="card-grid">
            <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                <p>Sorry, there was an error loading components.</p>
                <p style="font-size: 0.9em;">Please try refreshing the page or contact support if the problem persists.</p>
            </div>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)  # Return 200 to avoid HTMX error handling

@router.post("/api/components/", response_class=HTMLResponse)
async def create_component(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: str = Form(""),
    cost: float = Form(0.0),
    description: str = Form(""),
    notes: str = Form(""),
    vendorid: str = Form(""),
    pieceid: str = Form(""),
    image: Optional[UploadFile] = File(None)
):
    """API endpoint to create a new component."""
    # Convert HTML form data to proper types
    brand = brand.strip() or None
    description = description.strip() or None
    notes = notes.strip() or None
    vendorid_int = form_int_or_none(vendorid)
    pieceid_int = form_int_or_none(pieceid)
    
    processed_image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()
        processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
        if processed_image_bytes is None:
            vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
            pieces = session.exec(select(Piece).where(Piece.active == True)).all()
            return templates.TemplateResponse(
                "components/detail_main_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": Component(name=name, brand=brand, cost=dollars_to_cents(cost), description=description, notes=notes, vendorid=vendorid_int, pieceid=pieceid_int),
                 "vendors": vendors, "pieces": pieces, "form_action": "/api/components/", "edit_mode": True},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    cost_in_cents = dollars_to_cents(cost)
    
    new_component = Component(
        name=name, brand=brand, cost=cost_in_cents, description=description,
        notes=notes, vendorid=vendorid_int, pieceid=pieceid_int, image=processed_image_bytes
    )
    session.add(new_component)
    session.commit()
    session.refresh(new_component)

    response = RedirectResponse(url=f"/components/{new_component.comid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/components/{new_component.comid}" 
    return response


@router.put("/api/components/{comid}", response_class=HTMLResponse)
async def update_component(
    comid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: str = Form(""),
    cost: float = Form(0.0),
    description: str = Form(""),
    notes: str = Form(""),
    vendorid: str = Form(""),
    pieceid: str = Form(""),
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[str] = Form(None)
):
    """API endpoint to update an existing component. FIXED: Proper HTML form data handling."""
    
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    # Convert HTML form data to proper types
    brand = brand.strip() or None
    description = description.strip() or None
    notes = notes.strip() or None
    vendorid_int = form_int_or_none(vendorid)
    pieceid_int = form_int_or_none(pieceid)
    keep_image = form_bool(keep_existing_image)

    component.name = name
    component.brand = brand
    component.cost = dollars_to_cents(cost)
    component.description = description
    component.notes = notes
    component.vendorid = vendorid_int
    component.pieceid = pieceid_int

    if image and image.filename:
        image_bytes = await image.read()
        processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
        if processed_image_bytes is None:
            vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
            pieces = session.exec(select(Piece).where(Piece.active == True)).all()
            return templates.TemplateResponse(
                "components/detail_main_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": component, 
                 "vendors": vendors, "pieces": pieces, "form_action": f"/api/components/{comid}", "edit_mode": True},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        component.image = processed_image_bytes
    elif not keep_image:
        component.image = None

    session.add(component)
    session.commit()
    session.refresh(component)

    response = RedirectResponse(url=f"/components/{component.comid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/components/{component.comid}"
    return response

@router.delete("/api/components/{comid}")
async def delete_component(comid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete a component."""
    component_to_delete = session.get(Component, comid)
    if not component_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    component_to_delete.active = False
    session.add(component_to_delete)

    linked_outfits = session.exec(select(Out2Comp).where(Out2Comp.comid == comid)).all()
    for link in linked_outfits:
        link.active = False
        session.add(link)
    session.commit()

    response = HTMLResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = "/components/" 
    return response


@router.get("/api/components/{comid}/outfits", response_class=HTMLResponse)
async def get_outfits_using_component(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTMX endpoint to list outfits using a specific component."""
    component = session.get(Component, comid)
    if not component or not component.active:
        return HTMLResponse("<p class='text-center text-secondary'>Component not found or inactive.</p>")

    outfit_links_results = session.exec(
        select(Out2Comp, Outfit)
        .join(Outfit, Out2Comp.outid == Outfit.outid)
        .where(Out2Comp.comid == comid, Out2Comp.active == True, Outfit.active == True)
    ).all()

    outfits = [result.Outfit for result in outfit_links_results if result.Outfit]

    for outfit_item in outfits:
        components_in_outfit_assoc = session.exec(
            select(Out2Comp, Component)
            .join(Component, Out2Comp.comid == Component.comid)
            .where(Out2Comp.outid == outfit_item.outid, Out2Comp.active == True, Component.active == True)
        ).all()
        outfit_item.totalcost = sum(assoc.Component.cost for assoc in components_in_outfit_assoc if assoc.Component)
    
    if outfits:
        return templates.TemplateResponse(
            "outfits/list_content.html", 
            {"request": request, "outfits": outfits}
        )
    else:
        return HTMLResponse("<p class='text-center text-secondary'>No active outfits found using this component.</p>")