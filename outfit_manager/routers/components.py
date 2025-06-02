# File: routers/components.py
# Revision: 1.0 - Component CRUD endpoints and HTML views

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime

from models import Component, Vendor, Piece
from models.database import get_session
from services.image_service import ImageService # Import the image service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency for common template context
async def get_template_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    return {"request": request, "vendors": vendors, "pieces": pieces}

# --- HTML Page Endpoints ---

@router.get("/components/", response_class=HTMLResponse)
async def list_components_page(request: Request):
    """HTML page to list components."""
    return templates.TemplateResponse(
        "components/list.html", {"request": request}
    )

@router.get("/components/new", response_class=HTMLResponse)
async def create_component_page(request: Request, context: dict = Depends(get_template_context)):
    """HTML page to create a new component."""
    return templates.TemplateResponse(
        "components/detail.html", {**context, "component": None, "edit_mode": True, "form_action": "/api/components/"}
    )

@router.get("/components/{comid}", response_class=HTMLResponse)
async def get_component_page(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific component."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    return templates.TemplateResponse(
        "components/detail.html", {"request": request, "component": component, "edit_mode": False}
    )

@router.get("/components/{comid}/edit", response_class=HTMLResponse)
async def edit_component_page(comid: int, request: Request, context: dict = Depends(get_template_context), session: Session = Depends(get_session)):
    """HTML page to edit a specific component."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")
    return templates.TemplateResponse(
        "components/detail.html", {**context, "component": component, "edit_mode": True, "form_action": f"/api/components/{comid}"}
    )

# --- HTMX/API Endpoints (returning HTML fragments or JSON) ---

@router.get("/api/components/", response_class=HTMLResponse)
async def list_components_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None, # Search query
    vendorid: Optional[int] = None,
    pieceid: Optional[int] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    """API endpoint to list components (HTMX fragment)."""
    query = select(Component).where(Component.active == True)

    if q:
        query = query.where(Component.name.contains(q) | Component.description.contains(q) | Component.brand.contains(q))
    if vendorid:
        query = query.where(Component.vendorid == vendorid)
    if pieceid:
        query = query.where(Component.pieceid == pieceid)

    # Sorting
    if sort_by == "name":
        query = query.order_by(Component.name if sort_order == "asc" else Component.name.desc())
    elif sort_by == "cost":
        query = query.order_by(Component.cost if sort_order == "asc" else Component.cost.desc())
    elif sort_by == "brand":
        query = query.order_by(Component.brand if sort_order == "asc" else Component.brand.desc())

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
    cost: int = Form(0),
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
            # Handle image processing failure
            # For HTMX, we can return an error message in the form partial
            return templates.TemplateResponse(
                "forms/component_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": Component(name=name, brand=brand, cost=cost, description=description, notes=notes, vendorid=vendorid, pieceid=pieceid),
                 "vendors": session.exec(select(Vendor)).all(), "pieces": session.exec(select(Piece)).all()},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    new_component = Component(
        name=name,
        brand=brand,
        cost=cost,
        description=description,
        notes=notes,
        vendorid=vendorid,
        pieceid=pieceid,
        image=processed_image_bytes
    )
    session.add(new_component)
    session.commit()
    session.refresh(new_component)

    # HTMX response: Redirect or refresh part of the page
    response = RedirectResponse(url=f"/components/{new_component.comid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/components/{new_component.comid}" # For full page redirect with HTMX
    return response


@router.put("/api/components/{comid}", response_class=HTMLResponse)
async def update_component(
    comid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: int = Form(0),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    pieceid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[bool] = Form(False) # New field to indicate if existing image should be kept
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
            return templates.TemplateResponse(
                "forms/component_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "component": component, # Pass the current component data back
                 "vendors": session.exec(select(Vendor)).all(), "pieces": session.exec(select(Piece)).all()},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        component.image = processed_image_bytes
    elif not keep_existing_image: # If no new image and not keeping existing, clear it
        component.image = None

    session.add(component)
    session.commit()
    session.refresh(component)

    response = RedirectResponse(url=f"/components/{component.comid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/components/{component.comid}"
    return response

@router.delete("/api/components/{comid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_component(comid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete a component."""
    component = session.get(Component, comid)
    if not component:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Component not found")

    component.active = False # Soft delete
    session.add(component)
    session.commit()

    # For HTMX, redirect to the list page after deletion
    return RedirectResponse(url="/components/", status_code=status.HTTP_303_SEE_OTHER)

# Placeholder for outfits using component (will be implemented in Phase 3)
@router.get("/api/components/{comid}/outfits", response_class=HTMLResponse)
async def get_outfits_using_component(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTMX endpoint to list outfits using a specific component."""
    # This will be implemented in Phase 3
    # For now, return an empty list or a message
    return HTMLResponse("<p class='text-center text-secondary'>No outfits found using this component yet.</p>")

# HTMX endpoint to list outfits using component
@router.get("/api/components/{comid}/outfits", response_class=HTMLResponse)
async def get_outfits_using_component(comid: int, request: Request, session: Session = Depends(get_session)):
    """HTMX endpoint to list outfits using a specific component."""
    # Ensure the component exists and is active
    component = session.get(Component, comid)
    if not component or not component.active:
        return HTMLResponse("<p class='text-center text-secondary'>Component not found or inactive.</p>")

    # Fetch outfits linked to this component via Out2Comp, ensuring both outfit and link are active
    outfit_links = session.exec(
        select(Out2Comp, Outfit)
        .join(Outfit)
        .where(Out2Comp.comid == comid, Out2Comp.active == True, Outfit.active == True)
    ).all()

    # Extract the Outfit objects
    outfits = [link.outfit for link in outfit_links if link.outfit]

    # Calculate total cost on the fly for each outfit before rendering (if not already managed by CRUD)
    for outfit in outfits:
        outfit_components_assoc = session.exec(
            select(Out2Comp, Component).join(Component).where(Out2Comp.outid == outfit.outid, Out2Comp.active == True)
        ).all()
        outfit.totalcost = sum(o2c.component.cost for o2c in outfit_components_assoc if o2c.component)


    if outfits:
        # Re-use outfit_cards partial
        return templates.TemplateResponse(
            "outfits/list_content.html", {"request": request, "outfits": outfits} # Use list_content which expects 'outfits'
        )
    else:
        return HTMLResponse("<p class='text-center text-secondary'>No outfits found using this component yet.</p>")
