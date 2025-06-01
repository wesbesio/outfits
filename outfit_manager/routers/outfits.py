# File: routers/outfits.py
# Revision: 4.0 - Add multipart form data support for combined outfit+image creation

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

# [Keep existing GET endpoints]

@router.post("/")
async def create_outfit(
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
    
    # Create the outfit
    db_outfit = Outfit(**outfit_data)
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    
    # Process image if provided
    if file:
        try:
            processed_image = await ImageService.validate_and_process_image(file)
            db_outfit.image = processed_image
            db_outfit.modified = datetime.now()
            session.add(db_outfit)
            session.commit()
        except Exception as e:
            # Log the error but continue - outfit was created successfully
            print(f"Error processing image: {str(e)}")
    
    # Return HTMX redirect to outfits list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/outfits"
    return response

# [Keep the rest of the file unchanged]