# File: routers/components.py
# Revision: 1.0 - Component CRUD operations

from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List

from models import Component, Vendor, Piece
from models.database import get_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_components(request: Request, session: Session = Depends(get_session)):
    """List all components with filtering options."""
    components = session.exec(select(Component).where(Component.active == True)).all()
    return templates.TemplateResponse(
        "components/list_content.html", 
        {"request": request, "components": components}
    )

@router.post("/", response_class=HTMLResponse)
async def create_component(
    request: Request,
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: int = Form(0),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    piecid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Create a new component."""
    # TODO: Implement image processing
    image_data = None
    if file and file.content_type.startswith('image/'):
        image_data = await file.read()
    
    component = Component(
        name=name,
        brand=brand,
        cost=cost,
        description=description,
        notes=notes,
        vendorid=vendorid,
        piecid=piecid,
        image=image_data
    )
    
    session.add(component)
    session.commit()
    session.refresh(component)
    
    # Redirect to components list
    return templates.TemplateResponse(
        "components/list.html",
        {"request": request, "message": "Component created successfully"}
    )

@router.get("/{component_id}", response_class=HTMLResponse)
async def get_component(
    request: Request, 
    component_id: int, 
    session: Session = Depends(get_session)
):
    """Get component details."""
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return templates.TemplateResponse(
        "components/detail_content.html",
        {"request": request, "component": component}
    )
