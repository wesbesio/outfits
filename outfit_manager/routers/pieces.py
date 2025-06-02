# File: routers/pieces.py
# Revision: 1.1 - Add HTML response support for HTMX

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime

from models.database import get_session
from models import Piece, PieceCreate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get_pieces(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of piece types"""
    query = select(Piece)
    
    if active_only:
        query = query.where(Piece.active == True)
    
    query = query.offset(skip).limit(limit)
    pieces = session.exec(query).all()
    
    # Check if we need to return HTML
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    
    if is_htmx_request or wants_html:
        # Return HTML content
        content = templates.get_template("partials/piece_options.html").render({
            "request": request,
            "pieces": pieces
        })
        return HTMLResponse(content=content)
    
    return pieces

@router.get("/{piece_id}", response_model=Piece)
async def get_piece(piece_id: int, session: Session = Depends(get_session)):
    """Get single piece by ID"""
    piece = session.get(Piece, piece_id)
    if not piece:
        raise HTTPException(status_code=404, detail="Piece type not found")
    
    return piece

@router.post("/")
async def create_piece(piece: PieceCreate, session: Session = Depends(get_session)):
    """Create new piece type - returns HTMX redirect response"""
    # Check if piece with same name already exists
    existing = session.exec(
        select(Piece).where(Piece.name == piece.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="Piece type with this name already exists"
        )
    
    db_piece = Piece(**piece.model_dump())
    session.add(db_piece)
    session.commit()
    session.refresh(db_piece)
    
    # Return HTMX redirect to components list (where pieces are used)
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/components"
    return response

# HTMX specific endpoints for partial updates
@router.get("/", response_class=HTMLResponse, name="piece_options")
async def get_piece_options_html(
    request: Request,
    session: Session = Depends(get_session)
):
    """Get pieces as HTML options for select elements"""
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    
    return templates.TemplateResponse("partials/piece_options.html", {
        "request": request,
        "pieces": pieces
    })