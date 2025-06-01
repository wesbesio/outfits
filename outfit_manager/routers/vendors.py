# File: routers/vendors.py
# Revision: 2.0 - HTMX Navigation Refactor
# Updated: Added HTMX redirects, removed modal dependencies

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from models.database import get_session
from models import Vendor, VendorCreate, VendorUpdate

router = APIRouter()

@router.get("/", response_model=List[Vendor])
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Get list of vendors"""
    query = select(Vendor)
    
    if active_only:
        query = query.where(Vendor.active == True)
    
    query = query.offset(skip).limit(limit)
    vendors = session.exec(query).all()
    
    return vendors

@router.get("/{vendor_id}", response_model=Vendor)
async def get_vendor(vendor_id: int, session: Session = Depends(get_session)):
    """Get single vendor by ID"""
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return vendor

@router.post("/")
async def create_vendor(vendor: VendorCreate, session: Session = Depends(get_session)):
    """Create new vendor - returns HTMX redirect response"""
    # Check if vendor with same name already exists
    existing = session.exec(
        select(Vendor).where(Vendor.name == vendor.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Vendor with this name already exists"
        )
    
    db_vendor = Vendor(**vendor.model_dump())
    session.add(db_vendor)
    session.commit()
    session.refresh(db_vendor)
    
    # Return HTMX redirect to components list (where vendors are managed)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/components"
    return response

@router.put("/{vendor_id}")
async def update_vendor(
    vendor_id: int,
    vendor_update: VendorUpdate,
    session: Session = Depends(get_session)
):
    """Update vendor - returns HTMX redirect response"""
    db_vendor = session.get(Vendor, vendor_id)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Check name uniqueness if updating name
    update_data = vendor_update.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        existing = session.exec(
            select(Vendor).where(
                Vendor.name == update_data["name"],
                Vendor.venid != vendor_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Vendor with this name already exists"
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
    
    db_vendor.modified = datetime.now()
    session.add(db_vendor)
    session.commit()
    session.refresh(db_vendor)
    
    # Return HTMX redirect to components list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/components"
    return response

@router.delete("/{vendor_id}")
async def delete_vendor(vendor_id: int, session: Session = Depends(get_session)):
    """Delete vendor (soft delete)"""
    db_vendor = session.get(Vendor, vendor_id)
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Check if vendor is used by any components
    from models import Component
    components_using_vendor = session.exec(
        select(Component).where(
            Component.vendorid == vendor_id,
            Component.active == True
        )
    ).all()
    
    if components_using_vendor:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete vendor that is referenced by active components"
        )
    
    db_vendor.active = False
    db_vendor.modified = datetime.now()
    session.add(db_vendor)
    session.commit()
    
    return {"message": "Vendor deleted successfully"}

@router.get("/{vendor_id}/components")
async def get_vendor_components(
    vendor_id: int,
    session: Session = Depends(get_session)
):
    """Get all components from this vendor"""
    # Verify vendor exists
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    from models import Component
    components = session.exec(
        select(Component).where(
            Component.vendorid == vendor_id,
            Component.active == True
        )
    ).all()
    
    return {
        "vendor_name": vendor.name,
        "components": [
            {
                "comid": comp.comid,
                "name": comp.name,
                "cost": comp.cost,
                "has_image": comp.image is not None
            }
            for comp in components
        ],
        "count": len(components)
    }