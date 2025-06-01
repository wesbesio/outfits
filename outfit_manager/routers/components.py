# File: routers/components.py
# Revision: 4.0 - Add multipart form data support for combined component+image creation

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse, Response
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

# [Keep existing GET endpoints]

@router.post("/")
async def create_component(
    name: str = Form(...),
    cost: int = Form(...),
    active: bool = Form(True),
    flag: bool = Form(False),
    description: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    piecid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Create new component with optional image in one request"""
    # Validate vendor and piece if provided
    if vendorid:
        vendor = session.get(Vendor, vendorid)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
    
    if piecid:
        piece = session.get(Piece, piecid)
        if not piece:
            raise HTTPException(status_code=404, detail="Piece type not found")
    
    # Create component data
    component_data = {
        "name": name,
        "cost": cost,
        "active": active,
        "flag": flag,
        "description": description,
        "brand": brand,
        "notes": notes,
        "vendorid": vendorid,
        "piecid": piecid,
    }
    
    # Create the component
    db_component = Component(**component_data)
    session.add(db_component)
    session.commit()
    session.refresh(db_component)
    
    # Process image if provided
    if file:
        try:
            processed_image = await ImageService.validate_and_process_image(file)
            db_component.image = processed_image
            db_component.modified = datetime.now()
            session.add(db_component)
            session.commit()
        except Exception as e:
            # Log the error but continue - component was created successfully
            print(f"Error processing image: {str(e)}")
    
    # Return HTMX redirect to components list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/components"
    return response

# [Keep the rest of the file unchanged]