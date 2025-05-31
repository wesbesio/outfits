from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from models.database import get_session
from models import (
    Component, ComponentCreate, ComponentUpdate, ComponentResponse,
    Vendor, Piece, Out2Comp
)
from services.image_service import ImageService

router = APIRouter()

@router.get("/", response_model=List[ComponentResponse])
async def get_components(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    vendor_id: Optional[int] = None,
    piece_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get list of components with vendor and piece names"""
    query = select(Component, Vendor.name, Piece.name).outerjoin(
        Vendor, Component.vendorid == Vendor.venid
    ).outerjoin(
        Piece, Component.piecid == Piece.piecid
    )
    
    if active_only:
        query = query.where(Component.active == True)
    
    if vendor_id:
        query = query.where(Component.vendorid == vendor_id)
    
    if piece_id:
        query = query.where(Component.piecid == piece_id)
    
    query = query.offset(skip).limit(limit)
    results = session.exec(query).all()
    
    components = []
    for component, vendor_name, piece_name in results:
        comp_response = ComponentResponse(
            **component.model_dump(),
            has_image=component.image is not None,
            vendor_name=vendor_name,
            piece_name=piece_name
        )
        components.append(comp_response)
    
    return components

@router.get("/{component_id}", response_model=ComponentResponse)
async def get_component(component_id: int, session: Session = Depends(get_session)):
    """Get single component by ID"""
    query = select(Component, Vendor.name, Piece.name).outerjoin(
        Vendor, Component.vendorid == Vendor.venid
    ).outerjoin(
        Piece, Component.piecid == Piece.piecid
    ).where(Component.comid == component_id)
    
    result = session.exec(query).first()
    if not result:
        raise HTTPException(status_code=404, detail="Component not found")
    
    component, vendor_name, piece_name = result
    
    return ComponentResponse(
        **component.model_dump(),
        has_image=component.image is not None,
        vendor_name=vendor_name,
        piece_name=piece_name
    )

@router.post("/", response_model=ComponentResponse)
async def create_component(
    component: ComponentCreate, 
    session: Session = Depends(get_session)
):
    """Create new component"""
    # Validate vendor and piece if provided
    if component.vendorid:
        vendor = session.get(Vendor, component.vendorid)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
    
    if component.piecid:
        piece = session.get(Piece, component.piecid)
        if not piece:
            raise HTTPException(status_code=404, detail="Piece type not found")
    
    db_component = Component(**component.model_dump())
    session.add(db_component)
    session.commit()
    session.refresh(db_component)
    
    # Get vendor and piece names for response
    vendor_name = None
    piece_name = None
    
    if db_component.vendorid:
        vendor = session.get(Vendor, db_component.vendorid)
        vendor_name = vendor.name if vendor else None
    
    if db_component.piecid:
        piece = session.get(Piece, db_component.piecid)
        piece_name = piece.name if piece else None
    
    return ComponentResponse(
        **db_component.model_dump(),
        has_image=False,
        vendor_name=vendor_name,
        piece_name=piece_name
    )

@router.put("/{component_id}", response_model=ComponentResponse)
async def update_component(
    component_id: int,
    component_update: ComponentUpdate,
    session: Session = Depends(get_session)
):
    """Update component"""
    db_component = session.get(Component, component_id)
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Validate vendor and piece if being updated
    update_data = component_update.model_dump(exclude_unset=True)
    
    if "vendorid" in update_data and update_data["vendorid"]:
        vendor = session.get(Vendor, update_data["vendorid"])
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
    
    if "piecid" in update_data and update_data["piecid"]:
        piece = session.get(Piece, update_data["piecid"])
        if not piece:
            raise HTTPException(status_code=404, detail="Piece type not found")
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_component, field, value)
    
    db_component.modified = datetime.now()
    session.add(db_component)
    session.commit()
    session.refresh(db_component)
    
    # Get vendor and piece names for response
    vendor_name = None
    piece_name = None
    
    if db_component.vendorid:
        vendor = session.get(Vendor, db_component.vendorid)
        vendor_name = vendor.name if vendor else None
    
    if db_component.piecid:
        piece = session.get(Piece, db_component.piecid)
        piece_name = piece.name if piece else None
    
    return ComponentResponse(
        **db_component.model_dump(),
        has_image=db_component.image is not None,
        vendor_name=vendor_name,
        piece_name=piece_name
    )

@router.delete("/{component_id}")
async def delete_component(component_id: int, session: Session = Depends(get_session)):
    """Delete component (soft delete)"""
    db_component = session.get(Component, component_id)
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Check if component is used in any active outfits
    active_links = session.exec(
        select(Out2Comp).where(
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
    ).all()
    
    if active_links:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete component that is used in active outfits"
        )
    
    db_component.active = False
    db_component.modified = datetime.now()
    session.add(db_component)
    session.commit()
    
    return {"message": "Component deleted successfully"}

@router.post("/{component_id}/upload-image")
async def upload_component_image(
    component_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload image for component"""
    # Validate component exists
    db_component = session.get(Component, component_id)
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Validate and process image
    try:
        processed_image = await ImageService.validate_and_process_image(file)
        
        # Save image to database
        db_component.image = processed_image
        db_component.modified = datetime.now()
        session.add(db_component)
        session.commit()
        
        return {"message": "Image uploaded successfully", "has_image": True}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Image upload failed")

@router.delete("/{component_id}/image")
async def delete_component_image(
    component_id: int,
    session: Session = Depends(get_session)
):
    """Remove image from component"""
    db_component = session.get(Component, component_id)
    if not db_component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    db_component.image = None
    db_component.modified = datetime.now()
    session.add(db_component)
    session.commit()
    
    return {"message": "Image removed successfully", "has_image": False}

@router.get("/{component_id}/outfits")
async def get_component_outfits(
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get all outfits that contain this component"""
    # Verify component exists
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Get outfits through junction table
    query = select(Out2Comp).where(
        Out2Comp.comid == component_id,
        Out2Comp.active == True
    )
    
    links = session.exec(query).all()
    outfit_ids = [link.outid for link in links]
    
    return {"outfit_ids": outfit_ids, "count": len(outfit_ids)}