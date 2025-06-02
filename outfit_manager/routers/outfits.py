# File: routers/outfits.py
# Revision: 1.0 - Outfit CRUD endpoints and HTML views

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List
from collections import defaultdict

from models import Outfit, Component, Vendor, Out2Comp
from models.database import get_session
from services.image_service import ImageService # Re-use the image service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency for common template context
async def get_outfit_template_context(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    # Also fetch active components for outfit association
    components = session.exec(select(Component).where(Component.active == True)).all()
    return {"request": request, "vendors": vendors, "components": components}

# --- HTML Page Endpoints ---

@router.get("/outfits/", response_class=HTMLResponse)
async def list_outfits_page(request: Request):
    """HTML page to list outfits."""
    return templates.TemplateResponse(
        "outfits/list.html", {"request": request}
    )

@router.get("/outfits/new", response_class=HTMLResponse)
async def create_outfit_page(request: Request, context: dict = Depends(get_outfit_template_context)):
    """HTML page to create a new outfit."""
    return templates.TemplateResponse(
        "outfits/detail.html", {**context, "outfit": None, "edit_mode": True, "form_action": "/api/outfits/"}
    )

@router.get("/outfits/{outid}", response_class=HTMLResponse)
async def get_outfit_page(outid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific outfit."""
    outfit = session.get(Outfit, outid)
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")
    # Eager load components for display
    outfit_components = session.exec(
        select(Out2Comp, Component).join(Component).where(Out2Comp.outid == outid, Out2Comp.active == True)
    ).all()
    # Extract just the Component objects
    associated_components = [o2c.component for o2c in outfit_components if o2c.component]

    return templates.TemplateResponse(
        "outfits/detail.html", {"request": request, "outfit": outfit, "edit_mode": False, "associated_components": associated_components}
    )

@router.get("/outfits/{outid}/edit", response_class=HTMLResponse)
async def edit_outfit_page(outid: int, request: Request, context: dict = Depends(get_outfit_template_context), session: Session = Depends(get_session)):
    """HTML page to edit a specific outfit."""
    outfit = session.get(Outfit, outid)
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    # Get currently associated component IDs for form pre-selection
    current_component_ids = {
        o2c.comid for o2c in session.exec(select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)).all()
    }

    return templates.TemplateResponse(
        "outfits/detail.html", {**context, "outfit": outfit, "edit_mode": True, "form_action": f"/api/outfits/{outid}", "current_component_ids": current_component_ids}
    )

# --- HTMX/API Endpoints (returning HTML fragments or JSON) ---

@router.get("/api/outfits/", response_class=HTMLResponse)
async def list_outfits_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None, # Search query
    vendorid: Optional[int] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    """API endpoint to list outfits (HTMX fragment)."""
    query = select(Outfit).where(Outfit.active == True)

    if q:
        query = query.where(Outfit.name.contains(q) | Outfit.description.contains(q))
    if vendorid:
        query = query.where(Outfit.vendorid == vendorid)

    # Sorting
    if sort_by == "name":
        query = query.order_by(Outfit.name if sort_order == "asc" else Outfit.name.desc())
    elif sort_by == "totalcost":
        query = query.order_by(Outfit.totalcost if sort_order == "asc" else Outfit.totalcost.desc())

    outfits = session.exec(query).all()

    # Calculate total cost on the fly if it's not always updated by CRUD
    # This might be redundant if totalcost is managed during component association/dissociation
    for outfit in outfits:
        # Load components for each outfit to calculate cost, if not already relationship loaded
        outfit_components_assoc = session.exec(
            select(Out2Comp, Component).join(Component).where(Out2Comp.outid == outfit.outid, Out2Comp.active == True)
        ).all()
        outfit.totalcost = sum(o2c.component.cost for o2c in outfit_components_assoc if o2c.component)


    return templates.TemplateResponse(
        "outfits/list_content.html", {"request": request, "outfits": outfits}
    )


@router.post("/api/outfits/", response_class=HTMLResponse)
async def create_outfit(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    component_ids: List[int] = Form([]) # List of selected component IDs
):
    """API endpoint to create a new outfit."""
    processed_image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()
        processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
        if processed_image_bytes is None:
            return templates.TemplateResponse(
                "forms/outfit_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "outfit": Outfit(name=name, description=description, notes=notes, vendorid=vendorid),
                 "vendors": session.exec(select(Vendor)).all(),
                 "components": session.exec(select(Component).where(Component.active == True)).all(),
                 "current_component_ids": component_ids},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    new_outfit = Outfit(
        name=name,
        description=description,
        notes=notes,
        vendorid=vendorid,
        image=processed_image_bytes,
        totalcost=0 # Will be updated after components are added
    )
    session.add(new_outfit)
    session.commit()
    session.refresh(new_outfit)

    total_cost = 0
    # Associate components
    for comid in component_ids:
        component = session.get(Component, comid)
        if component and component.active:
            out2comp_link = Out2Comp(outid=new_outfit.outid, comid=comid)
            session.add(out2comp_link)
            total_cost += component.cost

    new_outfit.totalcost = total_cost
    session.add(new_outfit) # Add again to update totalcost
    session.commit()
    session.refresh(new_outfit)

    response = RedirectResponse(url=f"/outfits/{new_outfit.outid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/outfits/{new_outfit.outid}"
    return response


@router.put("/api/outfits/{outid}", response_class=HTMLResponse)
async def update_outfit(
    outid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[bool] = Form(False),
    component_ids: List[int] = Form([])
):
    """API endpoint to update an existing outfit."""
    outfit = session.get(Outfit, outid)
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    outfit.name = name
    outfit.description = description
    outfit.notes = notes
    outfit.vendorid = vendorid

    if image and image.filename:
        image_bytes = await image.read()
        processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
        if processed_image_bytes is None:
             return templates.TemplateResponse(
                "forms/outfit_form_content.html",
                {"request": request, "error": "Invalid or too large image file.",
                 "outfit": outfit,
                 "vendors": session.exec(select(Vendor)).all(),
                 "components": session.exec(select(Component).where(Component.active == True)).all(),
                 "current_component_ids": component_ids},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        outfit.image = processed_image_bytes
    elif not keep_existing_image:
        outfit.image = None

    # Manage component associations (Out2Comp)
    # Get current active associations
    current_associations = session.exec(
        select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)
    ).all()
    current_comid_set = {assoc.comid for assoc in current_associations}
    new_comid_set = set(component_ids)

    total_cost = 0
    # Components to add
    for comid in new_comid_set - current_comid_set:
        component = session.get(Component, comid)
        if component and component.active:
            out2comp_link = Out2Comp(outid=outid, comid=comid, active=True)
            session.add(out2comp_link)
            total_cost += component.cost

    # Components to remove (soft delete)
    for comid in current_comid_set - new_comid_set:
        # Find the specific Out2Comp link and soft delete it
        link_to_deactivate = session.exec(
            select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.comid == comid)
        ).first()
        if link_to_deactivate:
            link_to_deactivate.active = False
            session.add(link_to_deactivate)

    # Recalculate total cost from active components
    # (This ensures accuracy after adds/removes, and handles existing active components)
    active_outfit_components_assoc = session.exec(
        select(Out2Comp, Component).join(Component).where(Out2Comp.outid == outid, Out2Comp.active == True)
    ).all()
    outfit.totalcost = sum(o2c.component.cost for o2c in active_outfit_components_assoc if o2c.component)


    session.add(outfit)
    session.commit()
    session.refresh(outfit)

    response = RedirectResponse(url=f"/outfits/{outfit.outid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/outfits/{outfit.outid}"
    return response

@router.delete("/api/outfits/{outid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(outid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete an outfit."""
    outfit = session.get(Outfit, outid)
    if not outfit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    outfit.active = False # Soft delete
    session.add(outfit)
    session.commit()

    # Soft delete all associated Out2Comp entries for this outfit
    out2comp_links = session.exec(
        select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)
    ).all()
    for link in out2comp_links:
        link.active = False
        session.add(link)
    session.commit()

    return RedirectResponse(url="/outfits/", status_code=status.HTTP_303_SEE_OTHER)

# HTMX endpoint to list components for outfit form (for partial updates)
@router.get("/api/outfits/components_list", response_class=HTMLResponse)
async def get_available_components_for_outfit_form(
    request: Request,
    session: Session = Depends(get_session),
    outid: Optional[int] = None # Pass outid to know which are currently selected
):
    """
    Returns HTML fragment for component checkboxes,
    pre-selecting those already in the outfit.
    """
    all_components = session.exec(select(Component).where(Component.active == True)).all()
    current_component_ids = set()
    if outid:
        current_component_ids = {
            o2c.comid for o2c in session.exec(select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)).all()
        }

    return templates.TemplateResponse(
        "partials/component_checkboxes.html",
        {"request": request, "components": all_components, "current_component_ids": current_component_ids}
    )