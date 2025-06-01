from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from datetime import datetime
import os

from models.database import get_session
from models import Outfit, Component, Vendor, Piece

router = APIRouter()

# Fix template path - since this file is in routers/, we need to go up one level
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
templates_dir = os.path.join(parent_dir, "templates")

# Create templates instance with correct path
templates = Jinja2Templates(directory=templates_dir)

# Test endpoint
@router.get("/test/web-routes-working")
async def test_web_routes():
    return {"message": "Web routes working!", "status": "success"}

# Home page
@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# ===============================
# MAIN LIST PAGES
# ===============================

@router.get("/outfits", response_class=HTMLResponse)
async def outfits_list(request: Request):
    return templates.TemplateResponse("outfits/list.html", {"request": request})

@router.get("/components", response_class=HTMLResponse)
async def components_list(request: Request):
    return templates.TemplateResponse("components/list.html", {"request": request})

# ===============================
# DETAIL PAGES
# ===============================

@router.get("/outfits/{outfit_id}", response_class=HTMLResponse)
async def outfit_detail(outfit_id: int, request: Request, session: Session = Depends(get_session)):
    try:
        outfit = session.get(Outfit, outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        # Get related components through junction table
        from models import Out2Comp
        component_query = select(Component).join(Out2Comp).where(
            Out2Comp.outid == outfit_id,
            Out2Comp.active == True
        )
        components = session.exec(component_query).all()
        
        calculated_cost = sum(comp.cost for comp in components)
        component_count = len(components)
        
        outfit_data = {
            **outfit.model_dump(),
            "calculated_cost": calculated_cost,
            "component_count": component_count,
            "has_image": outfit.image is not None
        }
        
        return templates.TemplateResponse("outfits/detail.html", {
            "request": request,
            "outfit": outfit_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/components/{component_id}", response_class=HTMLResponse)
async def component_detail(component_id: int, request: Request, session: Session = Depends(get_session)):
    try:
        query = select(Component, Vendor.name, Piece.name).outerjoin(
            Vendor, Component.vendorid == Vendor.venid
        ).outerjoin(
            Piece, Component.piecid == Piece.piecid
        ).where(Component.comid == component_id)
        
        result = session.exec(query).first()
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        
        component, vendor_name, piece_name = result
        
        component_data = {
            **component.model_dump(),
            "has_image": component.image is not None,
            "vendor_name": vendor_name,
            "piece_name": piece_name
        }
        
        return templates.TemplateResponse("components/detail.html", {
            "request": request,
            "component": component_data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===============================
# FORM PAGES
# ===============================

@router.get("/outfits/new", response_class=HTMLResponse)
async def new_outfit_form(request: Request, session: Session = Depends(get_session)):
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        
        return templates.TemplateResponse("forms/outfit_form.html", {
            "request": request,
            "outfit": None,
            "vendors": vendors,
            "is_edit": False,
            "page_title": "Create New Outfit"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/components/new", response_class=HTMLResponse)
async def new_component_form(request: Request, session: Session = Depends(get_session)):
    try:
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        pieces = session.exec(select(Piece).where(Piece.active == True)).all()
        
        return templates.TemplateResponse("forms/component_form.html", {
            "request": request,
            "component": None,
            "vendors": vendors,
            "pieces": pieces,
            "is_edit": False,
            "page_title": "Create New Component"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor_form(request: Request):
    try:
        return templates.TemplateResponse("forms/vendor_form.html", {
            "request": request,
            "vendor": None,
            "is_edit": False,
            "page_title": "Create New Vendor"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===============================
# EDIT FORM PAGES
# ===============================

@router.get("/outfits/{outfit_id}/edit", response_class=HTMLResponse)
async def edit_outfit_form(outfit_id: int, request: Request, session: Session = Depends(get_session)):
    try:
        outfit = session.get(Outfit, outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        
        return templates.TemplateResponse("forms/outfit_form.html", {
            "request": request,
            "outfit": outfit,
            "vendors": vendors,
            "is_edit": True,
            "page_title": f"Edit {outfit.name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/components/{component_id}/edit", response_class=HTMLResponse)
async def edit_component_form(component_id: int, request: Request, session: Session = Depends(get_session)):
    try:
        component = session.get(Component, component_id)
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
        pieces = session.exec(select(Piece).where(Piece.active == True)).all()
        
        return templates.TemplateResponse("forms/component_form.html", {
            "request": request,
            "component": component,
            "vendors": vendors,
            "pieces": pieces,
            "is_edit": True,
            "page_title": f"Edit {component.name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/vendors/{vendor_id}/edit", response_class=HTMLResponse)
async def edit_vendor_form(vendor_id: int, request: Request, session: Session = Depends(get_session)):
    try:
        vendor = session.get(Vendor, vendor_id)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return templates.TemplateResponse("forms/vendor_form.html", {
            "request": request,
            "vendor": vendor,
            "is_edit": True,
            "page_title": f"Edit {vendor.name}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ===============================
# HTMX PARTIAL ENDPOINTS
# ===============================

@router.get("/api/outfits", response_class=HTMLResponse)
async def get_outfits_grid(request: Request, session: Session = Depends(get_session)):
    try:
        outfits = session.exec(select(Outfit).where(Outfit.active == True)).all()
        
        outfit_cards = []
        for outfit in outfits:
            # Get related components for cost calculation
            from models import Out2Comp
            component_query = select(Component).join(Out2Comp).where(
                Out2Comp.outid == outfit.outid,
                Out2Comp.active == True
            )
            components = session.exec(component_query).all()
            
            calculated_cost = sum(comp.cost for comp in components)
            component_count = len(components)
            
            outfit_cards.append({
                **outfit.model_dump(),
                "calculated_cost": calculated_cost,
                "component_count": component_count,
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
        query = select(Component, Vendor.name, Piece.name).outerjoin(
            Vendor, Component.vendorid == Vendor.venid
        ).outerjoin(
            Piece, Component.piecid == Piece.piecid
        ).where(Component.active == True)
        
        results = session.exec(query).all()
        
        component_cards = []
        for component, vendor_name, piece_name in results:
            component_cards.append({
                **component.model_dump(),
                "has_image": component.image is not None,
                "vendor_name": vendor_name,
                "piece_name": piece_name
            })
        
        return templates.TemplateResponse("partials/component_cards.html", {
            "request": request,
            "components": component_cards
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading components: {str(e)}")

# ===============================
# BACKWARD COMPATIBILITY REDIRECTS
# ===============================

# Handle old modal-style URLs
@router.get("/forms/new-component")
async def redirect_new_component():
    return RedirectResponse("/components/new", status_code=302)

@router.get("/forms/new-outfit") 
async def redirect_new_outfit():
    return RedirectResponse("/outfits/new", status_code=302)

@router.get("/forms/new-vendor")
async def redirect_new_vendor():
    return RedirectResponse("/vendors/new", status_code=302)