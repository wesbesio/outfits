from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from datetime import datetime

from models.database import get_session
from models import Outfit, Component, Vendor, Piece

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Test endpoint
@router.get("/test/web-routes-working")
async def test_web_routes():
    return {"message": "Web routes working!", "status": "success"}

# Redirect routes for old URLs
@router.get("/components/new")
async def redirect_component():
    return RedirectResponse("/forms/new-component", status_code=302)

@router.get("/outfits/new") 
async def redirect_outfit():
    return RedirectResponse("/forms/new-outfit", status_code=302)

@router.get("/vendors/new")
async def redirect_vendor():
    return RedirectResponse("/forms/new-vendor", status_code=302)

# Home page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# Main list pages
@router.get("/outfits", response_class=HTMLResponse)
async def outfits_list(request: Request):
    return templates.TemplateResponse("outfits/list.html", {"request": request})

@router.get("/components", response_class=HTMLResponse)
async def components_list(request: Request):
    return templates.TemplateResponse("components/list.html", {"request": request})

# Form endpoints
@router.get("/forms/new-component", response_class=HTMLResponse)
async def new_component_form(request: Request, session: Session = Depends(get_session)):
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        pieces = session.exec(select(Piece).where(Piece.active == True)).all()
        
        return templates.TemplateResponse("partials/component_form.html", {
            "request": request,
            "component": None,
            "vendors": vendors,
            "pieces": pieces,
            "is_edit": False
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/forms/new-outfit", response_class=HTMLResponse)
async def new_outfit_form(request: Request, session: Session = Depends(get_session)):
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        
        return templates.TemplateResponse("partials/outfit_form.html", {
            "request": request,
            "outfit": None,
            "vendors": vendors,
            "is_edit": False
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/forms/new-vendor", response_class=HTMLResponse)
async def new_vendor_form(request: Request):
    try:
        return templates.TemplateResponse("partials/vendor_form.html", {
            "request": request,
            "vendor": None,
            "is_edit": False
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Simple API endpoints for HTMX
@router.get("/api/outfits", response_class=HTMLResponse)
async def get_outfits_grid(request: Request, session: Session = Depends(get_session)):
    try:
        outfits = session.exec(select(Outfit).where(Outfit.active == True)).all()
        
        outfit_cards = []
        for outfit in outfits:
            outfit_cards.append({
                **outfit.model_dump(),
                "calculated_cost": 0,  # Simplified for now
                "component_count": 0,
                "has_image": outfit.image is not None,
                "creation_formatted": outfit.creation.strftime('%b %d, %Y') if outfit.creation else 'Unknown'
            })
        
        return templates.TemplateResponse("partials/outfit_cards.html", {
            "request": request,
            "outfits": outfit_cards
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading outfits: {str(e)}")

@router.get("/api/components", response_class=HTMLResponse) 
async def get_components_grid(request: Request, session: Session = Depends(get_session)):
    try:
        components = session.exec(select(Component).where(Component.active == True)).all()
        
        component_cards = []
        for component in components:
            component_cards.append({
                **component.model_dump(),
                "has_image": component.image is not None,
                "vendor_name": None,  # Simplified for now
                "piece_name": None
            })
        
        return templates.TemplateResponse("partials/component_cards.html", {
            "request": request,
            "components": component_cards
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading components: {str(e)}")