# File: routers/vendors.py
# Revision: 2.1 - Add HTML response support for HTMX

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import Response, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime

from models.database import get_session
from models import Vendor, VendorCreate, VendorUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_model=List[Vendor])
async def get_vendors(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of vendors"""
    query = select(Vendor)
    
    if active_only:
        query = query.where(Vendor.active == True)
    
    query = query.offset(skip).limit(limit)
    vendors = session.exec(query).all()
    
    # Check if we need to return HTML (for select options)
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    
    if is_htmx_request or wants_html:
        # Return vendor options HTML
        content = templates.get_template("partials/vendor_options.html").render({
            "request": request,
            "vendors": vendors
        })
        return HTMLResponse(content=content)
    
    return vendors