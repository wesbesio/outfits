# File: routers/outfits.py
# Revision: 4.2 - Fix HTML response support for HTMX and add error handling

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func
from typing import List, Optional, Union
from datetime import datetime
import traceback

from models.database import get_session
from models import (
    Outfit, OutfitCreate, OutfitUpdate, OutfitResponse,
    Out2Comp, Component
)
from services.image_service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get_outfits(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    sort_by: str = "name",
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of outfits with optional filtering and sorting"""
    # Debug information
    print(f"GET /api/outfits/ request received")
    print(f"Headers: Accept={accept}")
    print(f"Query params: sort_by={sort_by}, active_only={active_only}")
    
    query = select(Outfit)
    
    # Apply filters
    if active_only:
        query = query.where(Outfit.active == True)
    
    # Apply sorting
    if sort_by == "cost":
        query = query.order_by(Outfit.totalcost.desc())
    elif sort_by == "created":
        query = query.order_by(Outfit.creation.desc())
    elif sort_by == "modified":
        query = query.order_by(Outfit.modified.desc())
    else:  # Default to name
        query = query.order_by(Outfit.name)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    outfits = session.exec(query).all()
    
    # Enhanced outfit responses with calculated costs and component counts
    outfit_responses = []
    for outfit in outfits:
        # Get components for this outfit
        components_query = select(Component).join(Out2Comp).where(
            Out2Comp.outid == outfit.outid,
            Out2Comp.active == True
        )
        components = session.exec(components_query).all()
        
        # Calculate total cost of components
        calculated_cost = sum(comp.cost for comp in components)
        
        # Format creation date
        creation_formatted = outfit.creation.strftime("%b %d, %Y") if outfit.creation else None
        
        outfit_response = OutfitResponse(
            **outfit.model_dump(),
            has_image=outfit.image is not None,
            calculated_cost=calculated_cost,
            component_count=len(components),
        )
        outfit_response.creation_formatted = creation_formatted  # Add custom field
        outfit_responses.append(outfit_response)
    
    # Determine if we need to return HTML or JSON
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    
    if is_htmx_request or wants_html:
        print("Returning HTML response for outfits list")
        # Return HTML content from template
        content = templates.get_template("partials/outfit_cards.html").render({
            "request": request, 
            "outfits": outfit_responses
        })
        return HTMLResponse(content=content)
    
    print("Returning JSON response for outfits list")
    return outfit_responses

@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(outfit_id: int, session: Session = Depends(get_session)):
    """Get single outfit by ID"""
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Get components for this outfit
    components_query = select(Component).join(Out2Comp).where(
        Out2Comp.outid == outfit_id,
        Out2Comp.active == True
    )
    components = session.exec(components_query).all()
    
    # Calculate total cost of components
    calculated_cost = sum(comp.cost for comp in components)
    
    return OutfitResponse(
        **outfit.model_dump(),
        has_image=outfit.image is not None,
        calculated_cost=calculated_cost,
        component_count=len(components)
    )

@router.post("/")
async def create_outfit(
    request: Request,
    name: str = Form(...),
    active: bool = Form(True),
    flag: bool = Form(False),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Create new outfit with optional image in one request"""
    try:
        # Print received data for debugging
        print(f"Received outfit creation request: name={name}, vendorid={vendorid}")
        
        # Create outfit data
        outfit_data = {
            "name": name,
            "active": active,
            "flag": flag,
            "description": description,
            "notes": notes,
            "vendorid": vendorid,
            "totalcost": 0  # Will be calculated later
        }
        
        print(f"Creating outfit with data: {outfit_data}")
        
        # Create the outfit
        db_outfit = Outfit(**outfit_data)
        session.add(db_outfit)
        session.commit()
        session.refresh(db_outfit)
        
        print(f"Outfit created with ID: {db_outfit.outid}")
        
        # Process image if provided
        if file and file.filename:
            try:
                print(f"Processing image: {file.filename}")
                processed_image = await ImageService.validate_and_process_image(file)
                db_outfit.image = processed_image
                db_outfit.modified = datetime.now()
                session.add(db_outfit)
                session.commit()
                print("Image processed and saved successfully")
            except Exception as img_error:
                # Log the error but continue - outfit was created successfully
                print(f"Error processing image: {str(img_error)}")
                traceback.print_exc()
        
        # Return HTMX redirect to outfits list
        response = Response(status_code=200)
        response.headers["HX-Redirect"] = "/outfits"
        return response
        
    except Exception as e:
        print(f"Error creating outfit: {str(e)}")
        traceback.print_exc()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create outfit: {str(e)}"
        )

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
    for field, value in outfit_update.model_dump(exclude_unset=True).items():
        setattr(db_outfit, field, value)
    
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    
    # Return HTMX redirect to outfit detail
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = f"/outfits/{outfit_id}"
    return response

@router.post("/{outfit_id}/upload-image")
async def upload_outfit_image(
    outfit_id: int,
    file: UploadFile,
    session: Session = Depends(get_session)
):
    """Upload image for an outfit"""
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Process image
    processed_image = await ImageService.validate_and_process_image(file)
    
    # Update outfit
    db_outfit.image = processed_image
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    
    return {"message": "Image uploaded successfully"}

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

@router.delete("/{outfit_id}/image")
async def delete_outfit_image(outfit_id: int, session: Session = Depends(get_session)):
    """Delete image from outfit"""
    db_outfit = session.get(Outfit, outfit_id)
    if not db_outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if not db_outfit.image:
        raise HTTPException(status_code=404, detail="Outfit has no image to delete")
    
    db_outfit.image = None
    db_outfit.modified = datetime.now()
    session.add(db_outfit)
    session.commit()
    
    return {"message": "Image deleted successfully"}

@router.post("/{outfit_id}/components/{component_id}")
async def add_component_to_outfit(
    outfit_id: int,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Add component to outfit"""
    # Check if outfit exists
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Check if component exists
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Check if relationship already exists
    existing_relation = session.exec(
        select(Out2Comp).where(
            Out2Comp.outid == outfit_id,
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
    ).first()
    
    if existing_relation:
        # Already exists, do nothing
        return {"message": "Component already in outfit"}
    
    # Create new relationship
    relation = Out2Comp(
        outid=outfit_id,
        comid=component_id,
        active=True,
        flag=False
    )
    
    session.add(relation)
    
    # Update outfit total cost
    outfit.totalcost = outfit.totalcost + component.cost
    outfit.modified = datetime.now()
    session.add(outfit)
    
    session.commit()
    
    return {"message": "Component added to outfit successfully"}

@router.delete("/{outfit_id}/components/{component_id}")
async def remove_component_from_outfit(
    outfit_id: int,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Remove component from outfit (soft delete the relationship)"""
    # Check if outfit exists
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Check if component exists
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Check if relationship exists
    relation = session.exec(
        select(Out2Comp).where(
            Out2Comp.outid == outfit_id,
            Out2Comp.comid == component_id,
            Out2Comp.active == True
        )
    ).first()
    
    if not relation:
        raise HTTPException(status_code=404, detail="Component not in outfit")
    
    # Soft delete the relationship
    relation.active = False
    relation.modified = datetime.now()
    session.add(relation)
    
    # Update outfit total cost
    outfit.totalcost = outfit.totalcost - component.cost
    outfit.modified = datetime.now()
    session.add(outfit)
    
    session.commit()
    
    return {"message": "Component removed from outfit successfully"}

@router.get("/{outfit_id}/components", response_class=HTMLResponse)
async def get_outfit_components_html(
    request: Request,
    outfit_id: int,
    session: Session = Depends(get_session)
):
    """Get components in an outfit as HTML"""
    # Check if outfit exists
    outfit = session.get(Outfit, outfit_id)
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    # Get components for this outfit
    components_query = select(Component).join(Out2Comp).where(
        Out2Comp.outid == outfit_id,
        Out2Comp.active == True
    )
    components = session.exec(components_query).all()
    
    # Enhance components with additional information
    enhanced_components = []
    for component in components:
        enhanced_components.append({
            "comid": component.comid,
            "name": component.name,
            "brand": component.brand,
            "cost": component.cost,
            "has_image": component.image is not None,
            "vendor_name": component.vendor.name if component.vendor else None,
            "piece_name": component.piece.name if component.piece else None
        })
    
    # Return HTML template
    return templates.TemplateResponse("partials/outfit_components.html", {
        "request": request,
        "outfit": outfit,
        "components": enhanced_components,
        "total_cost": sum(comp["cost"] for comp in enhanced_components)
    })