# File: routers/components.py
# Revision: 4.2 - Fix HTML rendering for components list

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime
import traceback

from models.database import get_session
from models import (
    Component, ComponentCreate, ComponentUpdate, ComponentResponse,
    Vendor, Piece, Out2Comp
)
from services.image_service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=Union[List[ComponentResponse], HTMLResponse])
async def get_components(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    sort_by: str = "name",
    filter_vendor: Optional[int] = None,
    filter_piece: Optional[int] = None,
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of components with optional filtering and sorting"""
    # Debug information
    print(f"GET /api/components request received")
    print(f"Headers: Accept={accept}")
    print(f"Query params: sort_by={sort_by}, active_only={active_only}")
    print(f"Filter params: vendor={filter_vendor}, piece={filter_piece}")
    
    query = select(Component)
    
    # Apply filters
    if active_only:
        query = query.where(Component.active == True)
    
    if filter_vendor:
        query = query.where(Component.vendorid == filter_vendor)
    
    if filter_piece:
        query = query.where(Component.piecid == filter_piece)
    
    # Apply sorting
    if sort_by == "cost":
        query = query.order_by(Component.cost.desc())
    elif sort_by == "brand":
        query = query.order_by(Component.brand)
    elif sort_by == "created":
        query = query.order_by(Component.creation.desc())
    elif sort_by == "modified":
        query = query.order_by(Component.modified.desc())
    else:  # Default to name
        query = query.order_by(Component.name)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    components = session.exec(query).all()
    
    # Prepare component responses with additional data
    component_responses = []
    for component in components:
        component_response = ComponentResponse(
            **component.model_dump(),
            has_image=component.image is not None,
            vendor_name=component.vendor.name if component.vendor else None,
            piece_name=component.piece.name if component.piece else None
        )
        component_responses.append(component_response)
    
    # Determine if we need to return HTML or JSON
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    print(f"Is HTMX request: {is_htmx_request}, Wants HTML: {wants_html}")
    
    if is_htmx_request or wants_html:
        print("Returning HTML response")
        # Return HTML content from template
        content = templates.get_template("partials/component_cards.html").render({
            "request": request, 
            "components": component_responses
        })
        return HTMLResponse(content=content)
    else:
        print("Returning JSON response")
        # Return JSON response
        return component_responses