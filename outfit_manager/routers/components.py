# File: routers/components.py
# Revision: 1.1 - Updated list_components_page for HX-Request header

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List

from models import Component, Vendor, Piece, Outfit, Out2Comp
from models.database import get_session
from services.image_service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency for common template context (used for forms and potentially detail views)
async def get_form_template_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    return {"request": request, "vendors": vendors, "pieces": pieces}

# --- HTML Page Endpoints ---

@router.get("/components/", response_class=HTMLResponse)
async def list_components_page(request: Request, session: Session = Depends(get_session)): # Added session
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
        return templates.TemplateResponse("forms/component_form_content.html", template_vars)
    return templates.TemplateResponse("components/detail.html", template_vars) # components/detail.html acts as the form host

@router.get("/components/{comid}", response_class=HTMLResponse)
async def get_component_page(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific component. Handles HX-Request for partial updates."""
    component = session.get(Component, comid)
    if not component:
        # For HTMX, we might want to return a specific error partial or an empty response with a 404
        # For now, let FastAPI handle the 404, which HTMX can catch with responseError
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    
    template_vars = {"request": request, "component": component, "edit_mode": False}
    
    if request.headers.get("hx-request"):
        # When loading component detail via HTMX into #main-content
        return templates.TemplateResponse("components/detail_content.html", template_vars)
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
        return templates.TemplateResponse("forms/component_form_content.html", template_vars)
    return templates.TemplateResponse("components/detail.html", template_vars) # components/detail.html acts as the form host


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
    # Pass vendors and pieces to the list_content template if it uses partials that need them
    # However, component_cards.html does not seem to need them directly.
    return templates.TemplateResponse(
        "components/list_content.html", {"request": request, "components": components}
    )

@router.post("/api/components/", response_class=HTMLResponse)
async def create_component(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: int = Form(0), # Assuming cost is submitted as integer cents
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
                "forms/component_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": Component(name=name, brand=brand, cost=cost, description=description, notes=notes, vendorid=vendorid, pieceid=pieceid),
                 "vendors": vendors, "pieces": pieces, "form_action": "/api/components/"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    new_component = Component(
        name=name, brand=brand, cost=cost, description=description,
        notes=notes, vendorid=vendorid, pieceid=pieceid, image=processed_image_bytes
    )
    session.add(new_component)
    session.commit()
    session.refresh(new_component)

    # After successful creation, redirect to the new component's detail page
    # HTMX will follow this redirect if HX-Redirect header is present.
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
    cost: int = Form(0), # Assuming cost is submitted as integer cents
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
    component.cost = cost
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
                "forms/component_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": component, 
                 "vendors": vendors, "pieces": pieces, "form_action": f"/api/components/{comid}"},
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

@router.delete("/api/components/{comid}") # Removed default status_code for HTMX redirect
async def delete_component(comid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete a component."""
    component_to_delete = session.get(Component, comid)
    if not component_to_delete:
        # For HTMX, even on 404, if the client expects a redirect or specific handling,
        # you might return a response that HTMX can use.
        # However, raising an HTTP 404 is standard.
        # If HX-Target is body, this will trigger htmx:responseError
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    component_to_delete.active = False
    session.add(component_to_delete)

    linked_outfits = session.exec(select(Out2Comp).where(Out2Comp.comid == comid)).all()
    for link in linked_outfits:
        link.active = False
        session.add(link)
    session.commit()

    # For HTMX, to refresh the list page (assuming it's the target or pushed URL)
    response = HTMLResponse(content="", status_code=status.HTTP_204_NO_CONTENT) # Standard for DELETE
    # Tell HTMX to redirect to the components list page after successful deletion.
    # This assumes the hx-target of the delete button was something like the body or #main-content
    # and that a full page refresh/navigation is desired.
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
            {"request": request, "outfits": outfits} # Reuses outfit_cards via outfits/list_content
        )
    else:
        return HTMLResponse("<p class='text-center text-secondary'>No active outfits found using this component.</p>")

