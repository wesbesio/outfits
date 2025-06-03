# File: routers/components.py
# Revision: 1.2 - Fixed HTMX template routing and cost handling (dollars/cents consistency)

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from typing import Optional, List

from models import Component, Vendor, Piece, Outfit, Out2Comp
from models.database import get_session
from services.image_service import ImageService
from services.template_service import templates

router = APIRouter()

# Helper function to convert dollars to cents for storage
def dollars_to_cents(dollars: float) -> int:
    """Convert dollars to cents for database storage."""
    return int(round(dollars * 100))

# Helper function to convert cents to dollars for display
def cents_to_dollars(cents: int) -> float:
    """Convert cents to dollars for display."""
    return cents / 100.0

# Dependency for common template context (used for forms and potentially detail views)
async def get_form_template_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    return {"request": request, "vendors": vendors, "pieces": pieces}

# --- HTML Page Endpoints ---

@router.get("/components/", response_class=HTMLResponse)
async def list_components_page(request: Request, session: Session = Depends(get_session)):
    """HTML page to list components. Returns full page or content block based on HX-Request."""
    # Context needed for the filter bar in both full page and partial content
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    context = {"request": request, "vendors": vendors, "pieces": pieces}

    if request.headers.get("hx-request"):
        # If it's an HTMX request, return only the main content block
        return templates.TemplateResponse("components/list_main_content.html", context)
    
    # Otherwise, return the full page
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
        # FIXED: Use detail_main_content.html instead of detail_content.html for HTMX requests
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
    vendorid: Optional[int] = None,
    pieceid: Optional[int] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    """API endpoint to list components (HTMX fragment for the card grid)."""
    query = select(Component).where(Component.active == True)

    if q:
        query = query.where(Component.name.ilike(f"%{q}%") | Component.description.ilike(f"%{q}%") | Component.brand.ilike(f"%{q}%"))
    if vendorid:
        query = query.where(Component.vendorid == vendorid)
    if pieceid:
        query = query.where(Component.pieceid == pieceid)

    sort_field = getattr(Component, sort_by, Component.name)
    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
        
    components = session.exec(query).all()
    return templates.TemplateResponse(
        "components/list_content.html", {"request": request, "components": components}
    )

@router.post("/api/components/", response_class=HTMLResponse)
async def create_component(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: float = Form(0.0),  # FIXED: Accept dollars as float
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    pieceid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """API endpoint to create a new component."""
    processed_image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()
        processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
        if processed_image_bytes is None:
            vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
            pieces = session.exec(select(Piece).where(Piece.active == True)).all()
            # Re-render the form content with the error
            return templates.TemplateResponse(
                "components/detail_main_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": Component(name=name, brand=brand, cost=dollars_to_cents(cost), description=description, notes=notes, vendorid=vendorid, pieceid=pieceid),
                 "vendors": vendors, "pieces": pieces, "form_action": "/api/components/", "edit_mode": True},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    # FIXED: Convert dollars to cents for storage
    cost_in_cents = dollars_to_cents(cost)
    
    new_component = Component(
        name=name, brand=brand, cost=cost_in_cents, description=description,
        notes=notes, vendorid=vendorid, pieceid=pieceid, image=processed_image_bytes
    )
    session.add(new_component)
    session.commit()
    session.refresh(new_component)

    # After successful creation, redirect to the new component's detail page
    response = RedirectResponse(url=f"/components/{new_component.comid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/components/{new_component.comid}" 
    return response


@router.put("/api/components/{comid}", response_class=HTMLResponse)
async def update_component(
    comid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: float = Form(0.0),  # FIXED: Accept dollars as float
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    pieceid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[bool] = Form(False)
):
    """API endpoint to update an existing component."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    component.name = name
    component.brand = brand
    component.cost = dollars_to_cents(cost)  # FIXED: Convert dollars to cents
    component.description = description
    component.notes = notes
    component.vendorid = vendorid
    component.pieceid = pieceid

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
    elif not keep_existing_image:
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

    # For HTMX, to refresh the list page
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