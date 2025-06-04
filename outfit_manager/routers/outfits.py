# File: routers/outfits.py
# Revision: 1.20 - Removed score label from increment/decrement endpoints

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from typing import Optional, List

from models import Outfit, Component, Vendor, Out2Comp, Piece
from models.database import get_session
from services.image_service import ImageService
from services.template_service import templates

router = APIRouter()

# Helper function to convert cents to dollars for display
def cents_to_dollars(cents: int) -> float:
    """Convert cents to dollars for display."""
    return cents / 100.0

async def get_outfit_form_context(request: Request, session: Session = Depends(get_session)):
    """Provides common context for outfit forms and detail pages."""
    all_active_components = session.exec(select(Component).where(Component.active == True).order_by(Component.name)).all()
    return {"request": request, "all_active_components": all_active_components}

# IMPORTANT: More specific routes MUST come before less specific ones
# /outfits/new MUST come before /outfits/

@router.get("/outfits/new", response_class=HTMLResponse)
async def create_outfit_page(request: Request, context: dict = Depends(get_outfit_form_context)):
    """Serves the HTML page for creating a new outfit, adapting for HTMX requests."""
    print(f"🎯 CREATE OUTFIT PAGE CALLED - HX-Request: {request.headers.get('hx-request')}")  # Debug log
    
    template_vars = {
        "request": request,
        "components": context.get("all_active_components", []),
        "outfit": None,
        "edit_mode": True,
        "form_action": "/api/outfits/",
        "current_component_ids": set(),
        "error": None,
        "associated_components": []
    }

    if request.headers.get("hx-request"):
        print("🎯 Returning HTMX template: outfits/detail_main_content.html")  # Debug log
        return templates.TemplateResponse("outfits/detail_main_content.html", template_vars)
    
    print("🎯 Returning full page template: outfits/detail.html")  # Debug log
    return templates.TemplateResponse("outfits/detail.html", template_vars)

@router.get("/outfits/{outid}/edit", response_class=HTMLResponse)
async def edit_outfit_page(outid: int, request: Request, context: dict = Depends(get_outfit_form_context), session: Session = Depends(get_session)):
    """Serves the HTML page for editing an existing outfit, adapting for HTMX requests."""
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    current_component_ids = {
        link.comid for link in session.exec(
            select(Out2Comp).where(Out2Comp.outid == outid, Out2Comp.active == True)
        ).all()
    }
    template_vars = {
        "request": request,
        "components": context.get("all_active_components", []),
        "outfit": outfit,
        "edit_mode": True,
        "form_action": f"/api/outfits/{outid}",
        "current_component_ids": current_component_ids,
        "error": None,
        "associated_components": []
    }

    if request.headers.get("hx-request"):
        return templates.TemplateResponse("outfits/detail_main_content.html", template_vars)
    return templates.TemplateResponse("outfits/detail.html", template_vars)

@router.get("/outfits/{outid}", response_class=HTMLResponse)
async def get_outfit_page(outid: int, request: Request, session: Session = Depends(get_session)):
    """Serves the HTML page for viewing a specific outfit, adapting for HTMX requests."""
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    outfit_component_links = session.exec(
        select(Out2Comp, Component)
        .join(Component, Out2Comp.comid == Component.comid)
        .where(Out2Comp.outid == outid, Out2Comp.active == True, Component.active == True)
    ).all()
    associated_components = sorted([link.Component for link in outfit_component_links if link.Component], key=lambda c: c.name)
    outfit.totalcost = sum(comp.cost for comp in associated_components if comp)

    template_vars = {
        "request": request,
        "outfit": outfit,
        "edit_mode": False,
        "associated_components": associated_components
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("outfits/detail_main_content.html", template_vars)
    return templates.TemplateResponse("outfits/detail.html", template_vars)

@router.get("/outfits/", response_class=HTMLResponse)
async def list_outfits_page(request: Request, session: Session = Depends(get_session)):
    """Serves the full HTML page for listing outfits or just the main content block for HTMX requests."""
    print(f"🎯 LIST OUTFITS PAGE CALLED - HX-Request: {request.headers.get('hx-request')}")  # Debug log
    
    context = {"request": request}
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("outfits/list_main_content.html", context)
    return templates.TemplateResponse("outfits/list.html", context)

# --- API Endpoints ---
@router.get("/api/outfits/", response_class=HTMLResponse)
async def list_outfits_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc"
):
    query = select(Outfit).where(Outfit.active == True)
    if q:
        query = query.where(Outfit.name.ilike(f"%{q}%") | Outfit.description.ilike(f"%{q}%"))

    sort_field = getattr(Outfit, sort_by, Outfit.name)
    if sort_order == "desc":
        query = query.order_by(sort_field.desc())
    else:
        query = query.order_by(sort_field.asc())
    outfits = session.exec(query).all()

    for outfit_item in outfits:
        active_components_links = session.exec(
            select(Out2Comp, Component)
            .join(Component, Out2Comp.comid == Component.comid)
            .where(Out2Comp.outid == outfit_item.outid, Out2Comp.active == True, Component.active == True)
        ).all()
        outfit_item.totalcost = sum(link.Component.cost for link in active_components_links if link.Component)
    return templates.TemplateResponse("outfits/list_content.html", {"request": request, "outfits": outfits})

@router.post("/api/outfits/", response_class=HTMLResponse)
async def create_outfit(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    score: int = Form(0),  # Score parameter
    image: Optional[UploadFile] = File(None)
):
    processed_image_bytes = None
    form_render_context = await get_outfit_form_context(request, session)

    # Convert form data
    description = description.strip() or None
    notes = notes.strip() or None
    
    # Ensure score is not negative
    if score < 0:
        score = 0

    if image and image.filename:
        image_bytes = await image.read()
        if image_bytes:
            processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
            if processed_image_bytes is None:
                error_context = {
                    "request": request,
                    "components": form_render_context.get("all_active_components", []),
                    "error": "Invalid or too large image file. Max 5MB. Allowed: JPEG, PNG, WEBP, GIF.",
                    "outfit": Outfit(name=name, description=description, notes=notes, score=score),
                    "edit_mode": True,
                    "form_action": "/api/outfits/",
                    "current_component_ids": set(),
                    "associated_components": []
                }
                return templates.TemplateResponse("outfits/detail_main_content.html", error_context, status_code=status.HTTP_400_BAD_REQUEST)

    new_outfit = Outfit(
        name=name, description=description, notes=notes,
        score=score,  # Include score field
        image=processed_image_bytes, totalcost=0
    )
    session.add(new_outfit)
    session.commit()
    session.refresh(new_outfit)

    success_render_context = {
        "request": request,
        "components": form_render_context.get("all_active_components", []),
        "outfit": new_outfit,
        "edit_mode": True,
        "form_action": f"/api/outfits/{new_outfit.outid}",
        "current_component_ids": set(),
        "error": None,
        "associated_components": []
    }

    response = templates.TemplateResponse("outfits/detail_main_content.html", success_render_context)
    response.headers["HX-Push-Url"] = f"/outfits/{new_outfit.outid}/edit"
    return response

@router.put("/api/outfits/{outid}", response_class=HTMLResponse)
async def update_outfit(
    outid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    notes: str = Form(""),
    score: int = Form(0),  # Score parameter
    image: Optional[UploadFile] = File(None),
    keep_existing_image: Optional[str] = Form(None),
    component_ids: List[int] = Form([])
):
    outfit_to_update = session.get(Outfit, outid)
    if not outfit_to_update or not outfit_to_update.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")

    # Convert form data
    description = description.strip() or None
    notes = notes.strip() or None
    keep_image = keep_existing_image is not None and keep_existing_image.lower() in ("true", "on", "1", "yes")
    
    # Ensure score is not negative
    if score < 0:
        score = 0

    outfit_to_update.name = name
    outfit_to_update.description = description
    outfit_to_update.notes = notes
    outfit_to_update.score = score  # Update score field
    
    form_render_context = await get_outfit_form_context(request, session)

    if image and image.filename:
        image_bytes = await image.read()
        if image_bytes:
            processed_image_bytes = ImageService.validate_and_process_image(image_bytes, image.filename)
            if processed_image_bytes is None:
                error_context = {
                    "request": request,
                    "components": form_render_context.get("all_active_components", []),
                    "error": "Invalid or too large image file. Max 5MB. Allowed: JPEG, PNG, WEBP, GIF.",
                    "outfit": outfit_to_update,
                    "edit_mode": True,
                    "form_action": f"/api/outfits/{outid}",
                    "current_component_ids": set(component_ids),
                    "associated_components": []
                }
                return templates.TemplateResponse("outfits/detail_main_content.html", error_context, status_code=status.HTTP_400_BAD_REQUEST)
            outfit_to_update.image = processed_image_bytes
    elif not keep_image:
        outfit_to_update.image = None

    # Manage component associations
    existing_links = session.exec(select(Out2Comp).where(Out2Comp.outid == outid)).all()
    existing_comids_in_db = {link.comid: link for link in existing_links}
    selected_comids_from_form = set(component_ids)

    for comid_val, link_obj in existing_comids_in_db.items():
        if comid_val not in selected_comids_from_form:
            if link_obj.active:
                link_obj.active = False; session.add(link_obj)
        else:
            if not link_obj.active:
                link_obj.active = True; session.add(link_obj)

    for comid_val in selected_comids_from_form:
        if comid_val not in existing_comids_in_db:
            component_item = session.get(Component, comid_val)
            if component_item and component_item.active:
                new_link = Out2Comp(outid=outid, comid=comid_val, active=True)
                session.add(new_link)
    session.commit()

    # Recalculate total cost based on currently active associated components
    active_component_links = session.exec(
        select(Out2Comp, Component)
        .join(Component, Out2Comp.comid == Component.comid)
        .where(Out2Comp.outid == outid, Out2Comp.active == True, Component.active == True)
    ).all()
    outfit_to_update.totalcost = sum(link.Component.cost for link in active_component_links if link.Component)

    session.add(outfit_to_update)
    session.commit()
    session.refresh(outfit_to_update)

    # After successful update, render the detail view of the outfit
    final_associated_components = sorted([link.Component for link in active_component_links if link.Component], key=lambda c: c.name)
    detail_view_context = {
        "request": request,
        "outfit": outfit_to_update,
        "edit_mode": False,
        "associated_components": final_associated_components
    }
    
    response = templates.TemplateResponse("outfits/detail_main_content.html", detail_view_context)
    response.headers["HX-Push-Url"] = f"/outfits/{outfit_to_update.outid}"
    return response

@router.delete("/api/outfits/{outid}")
async def delete_outfit(request: Request, outid: int, session: Session = Depends(get_session)):
    outfit_to_delete = session.get(Outfit, outid)
    if not outfit_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found")

    outfit_to_delete.active = False
    session.add(outfit_to_delete)
    links_to_deactivate = session.exec(select(Out2Comp).where(Out2Comp.outid == outid)).all()
    for link in links_to_deactivate:
        if link.active:
            link.active = False; session.add(link)
    session.commit()
    
    list_context = {"request": request}
    
    response = templates.TemplateResponse("outfits/list_main_content.html", list_context)
    response.headers["HX-Push-Url"] = "/outfits/" 
    return response

@router.get("/api/outfits/components_list", response_class=HTMLResponse)
async def get_available_components_for_outfit_form(
    request: Request,
    session: Session = Depends(get_session),
    outid: Optional[str] = Query(None)
):
    all_active_components = session.exec(select(Component).where(Component.active == True).order_by(Component.name)).all()
    current_component_ids = set()
    numeric_outid: Optional[int] = None
    if outid is not None and outid.strip().isdigit():
        try:
            numeric_outid = int(outid.strip())
        except ValueError:
            numeric_outid = None

    if numeric_outid is not None:
        outfit_exists_check = session.get(Outfit, numeric_outid)
        if outfit_exists_check:
            current_component_ids = {
                link.comid for link in session.exec(
                    select(Out2Comp).where(Out2Comp.outid == numeric_outid, Out2Comp.active == True)
                ).all()
            }
    return templates.TemplateResponse(
        "partials/component_checkboxes.html",
        {"request": request, "components": all_active_components, "current_component_ids": current_component_ids}
    )

@router.post("/api/outfits/{outid}/score/increment", response_class=HTMLResponse)
async def increment_outfit_score(
    outid: int, 
    request: Request, 
    session: Session = Depends(get_session)
):
    """API endpoint to increment outfit score by 1."""
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")
    
    # Increment the score
    outfit.score += 1
    session.add(outfit)
    session.commit()
    session.refresh(outfit)
    
    # Return updated score display as HTML fragment (no label)
    score_html = f"""
    <div id="outfit-score-display" class="score-display">
        <div class="score-controls">
            <button class="btn btn-score-minus" 
                    hx-post="/api/outfits/{outfit.outid}/score/decrement" 
                    hx-target="#outfit-score-display" 
                    hx-swap="outerHTML"
                    {'disabled' if outfit.score <= 0 else ''}>
                <span class="score-icon">−</span>
            </button>
            <span class="score-value">{outfit.score}</span>
            <button class="btn btn-score-plus" 
                    hx-post="/api/outfits/{outfit.outid}/score/increment" 
                    hx-target="#outfit-score-display" 
                    hx-swap="outerHTML">
                <span class="score-icon">+</span>
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=score_html)

@router.post("/api/outfits/{outid}/score/decrement", response_class=HTMLResponse)
async def decrement_outfit_score(
    outid: int, 
    request: Request, 
    session: Session = Depends(get_session)
):
    """API endpoint to decrement outfit score by 1, minimum 0."""
    outfit = session.get(Outfit, outid)
    if not outfit or not outfit.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outfit not found or inactive")
    
    # Decrement the score, but don't go below 0
    if outfit.score > 0:
        outfit.score -= 1
        session.add(outfit)
        session.commit()
        session.refresh(outfit)
    
    # Return updated score display as HTML fragment (no label)
    score_html = f"""
    <div id="outfit-score-display" class="score-display">
        <div class="score-controls">
            <button class="btn btn-score-minus" 
                    hx-post="/api/outfits/{outfit.outid}/score/decrement" 
                    hx-target="#outfit-score-display" 
                    hx-swap="outerHTML"
                    {'disabled' if outfit.score <= 0 else ''}>
                <span class="score-icon">−</span>
            </button>
            <span class="score-value">{outfit.score}</span>
            <button class="btn btn-score-plus" 
                    hx-post="/api/outfits/{outfit.outid}/score/increment" 
                    hx-target="#outfit-score-display" 
                    hx-swap="outerHTML">
                <span class="score-icon">+</span>
            </button>
        </div>
    </div>
    """
    
    return HTMLResponse(content=score_html)