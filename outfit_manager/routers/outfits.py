# File: routers/outfits.py
# Revision: 2.0 - HTMX Navigation Refactor
# Updated: Removed modal dependencies, added HTMX redirects for form submissions

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime

from models.database import get_session
from models import (
    Outfit, OutfitCreate, OutfitUpdate, OutfitResponse,
    Out2Comp, Component
)
from services.image_service import ImageService

router = APIRouter()

@router.get("/", response_model=List[OutfitResponse])
async def get_outfits(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Get list of outfits with calculated costs"""
    query = select(Outfit)
    
    if active_only:
        query = query.where(Outfit.active == True)
    
    query = query.offset(skip).limit(limit)
    outfits = session.exec(query).all()
    
    # Calculate costs and component counts for each outfit
    response_outfits = []
    for outfit in outfits:
        # Get related components through junction table
        component_query = select(Component).join(Out2Comp).where(
            Out2Comp.outid == outfit.outid,
            Out2Comp.active == True
        )
        components = session.exec(component_query).all()
        
        calculated_cost = sum(comp.cost for comp in components)
        component_count = len(components)
        
        outfit_response = OutfitResponse(
            **outfit.model_dump(),
            calculated_cost=calculated_cost,
            component_count=component_count,
            has_image=outfit.image is not None
        )
        response_outfits.append(outfit_response)
    
    return response_outfits

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: int, session: Session = Depends(get_session)):
    """Get single outfit by ID"""
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Calculate cost and component count
    component_query = select(Component).join(Out2Comp).where(
        Out2Comp.outid == outfit_id,
        Out2Comp.active == True
    )
    components = session.exec(component_query).all()
    
    calculated_cost = sum(comp.cost for comp in components)
    component_count = len(components)
    
    return OutfitResponse(
        **outfit.model_dump(),
        calculated_cost=calculated_cost,
        component_count=component_count,
        has_image=outfit.image is not None
    )

@router.post("/")
async def create_outfit(outfit: OutfitCreate, session: Session = Depends(get_session)):
    """Create new outfit - returns HTMX redirect response"""
    db_outfit = Outfit(**outfit.model_dump())
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    
    # Return HTMX redirect to outfits list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/outfits"
    return response

@router.put("/{outfit_id}")
async def update_outfit(
    outfit_id: int, 
    outfit_update: OutfitUpdate, 
    session: Session = Depends(get_session)
):
    """Update outfit - returns HTMX redirect response"""
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Update fields
    update_data = outfit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_outfit, field, value)
    
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    
    # Return HTMX redirect to outfit detail
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/outfits/{outfit_id}"
    return response

@router.delete("/{outfit_id}")
async def delete_outfit(outfit_id: int, session: Session = Depends(get_session)):
    """Delete outfit (soft delete)"""
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    db_outfit.active = False
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    
    return {"message": "Outfit deleted successfully"}

@router.post("/{outfit_id}/upload-image")
async def upload_outfit_image(
    outfit_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload image for outfit"""
    # Validate outfit exists
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Validate and process image
    try:
        processed_image = await ImageService.validate_and_process_image(file)
        
        # Save image to database
        db_outfit.image = processed_image
        db_outfit.modified = datetime.now()
        session.add(db_outfit)
        session.commit()
        
        return {"message": "Image uploaded successfully", "has_image": True}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Image upload failed")

@router.delete("/{outfit_id}/image")
async def delete_outfit_image(
    outfit_id: int,
    session: Session = Depends(get_session)
):
    """Remove image from outfit"""
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    db_outfit.image = None
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    
    return {"message": "Image removed successfully", "has_image": False}

@router.get("/{outfit_id}/components")
async def get_outfit_components(
    outfit_id: int,
    session: Session = Depends(get_session)
):
    """Get all components for an outfit"""
    # Verify outfit exists
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Get components through junction table
    query = select(Component, Out2Comp.creation.label("added_date")).join(Out2Comp).where(
        Out2Comp.outid == outfit_id,
        Out2Comp.active == True
    )
    
    results = session.exec(query).all()
    
    components = []
    for component, added_date in results:
        comp_dict = component.model_dump()
        comp_dict["added_to_outfit"] = added_date
        comp_dict["has_image"] = component.image is not None
        components.append(comp_dict)
    
    return components

@router.post("/{outfit_id}/components/{component_id}")
async def add_component_to_outfit(
    outfit_id: int,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Add component to outfit"""
    # Verify both exist
    outfit = session.get(Outfit, outfit_id)
    component = session.get(Component, component_id)
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Check if relationship already exists
    existing = session.exec(
        select(Out2Comp).where(
            Out2Comp.outid == outfit_id,
            Out2Comp.comid == component_id
        )
    ).first()
    
    if existing:
        # Reactivate if exists but inactive
        existing.active = True
        existing.modified = datetime.now()
        session.add(existing)
    else:
        # Create new relationship
        new_link = Out2Comp(outid=outfit_id, comid=component_id)
        session.add(new_link)
    
    session.commit()
    return {"message": "Component added to outfit successfully"}

@router.delete("/{outfit_id}/components/{component_id}")
async def remove_component_from_outfit(
    outfit_id: int,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Remove component from outfit"""
    # Find and deactivate relationship
    link = session.exec(
        select(Out2Comp).where(
            Out2Comp.outid == outfit_id,
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Component not found in outfit")
    
    link.active = False
    link.modified = datetime.now()
    session.add(link)
    session.commit()
    
    return {"message": "Component removed from outfit successfully"}