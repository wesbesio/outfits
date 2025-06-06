# File: routers/pieces.py
# Revision: 1.0 - Complete piece type CRUD with HTML responses

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from typing import Optional, List

from models import Piece, Component
from models.database import get_session
from services.template_service import templates

router = APIRouter()

# Helper function to convert HTML checkbox to boolean
def form_bool(value: Optional[str]) -> bool:
    """Convert HTML checkbox value to boolean."""
    return value is not None and value.lower() in ("true", "on", "1", "yes")

# --- HTML Page Endpoints ---

@router.get("/pieces/", response_class=HTMLResponse)
async def list_pieces_page(request: Request, session: Session = Depends(get_session)):
    """HTML page to list pieces. Returns full page or content block based on HX-Request."""
    context = {"request": request}

    if request.headers.get("hx-request"):
        return templates.TemplateResponse("pieces/list_main_content.html", context)
    
    return templates.TemplateResponse("pieces/list.html", context)

@router.get("/pieces/new", response_class=HTMLResponse)
async def create_piece_page(request: Request):
    """HTML page to create a new piece. Handles HX-Request for partial updates."""
    template_vars = {
        "request": request, 
        "piece": None, 
        "edit_mode": True, 
        "form_action": "/api/pieces/"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("pieces/detail_main_content.html", template_vars)
    return templates.TemplateResponse("pieces/detail.html", template_vars)

@router.get("/pieces/{piecid}", response_class=HTMLResponse)
async def get_piece_page(piecid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to view a specific piece. Handles HX-Request for partial updates."""
    piece = session.get(Piece, piecid)
    if not piece:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece not found")
    
    template_vars = {"request": request, "piece": piece, "edit_mode": False}
    
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("pieces/detail_main_content.html", template_vars)
    return templates.TemplateResponse("pieces/detail.html", template_vars)

@router.get("/pieces/{piecid}/edit", response_class=HTMLResponse)
async def edit_piece_page(piecid: int, request: Request, session: Session = Depends(get_session)):
    """HTML page to edit a specific piece. Handles HX-Request for partial updates."""
    piece = session.get(Piece, piecid)
    if not piece:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece not found")

    template_vars = {
        "request": request, 
        "piece": piece, 
        "edit_mode": True, 
        "form_action": f"/api/pieces/{piecid}"
    }
    if request.headers.get("hx-request"):
        return templates.TemplateResponse("pieces/detail_main_content.html", template_vars)
    return templates.TemplateResponse("pieces/detail.html", template_vars)

# --- HTMX/API Endpoints (returning HTML fragments or JSON) ---

@router.get("/api/pieces/", response_class=HTMLResponse)
async def list_pieces_api(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = None,
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc",
    show_inactive: Optional[str] = None
):
    """API endpoint to list pieces (HTMX fragment for the card grid)."""
    
    try:
        # Build query with proper error handling
        query = select(Piece)
        
        # Apply active filter unless show_inactive is checked
        show_inactive_bool = form_bool(show_inactive)
        if not show_inactive_bool:
            query = query.where(Piece.active == True)

        # Apply search filter if provided
        if q:
            query = query.where(Piece.name.ilike(f"%{q}%") | Piece.description.ilike(f"%{q}%"))

        # Handle sorting with fallback to name if invalid sort_by
        valid_sort_fields = ['name', 'description']
        if sort_by not in valid_sort_fields:
            sort_by = 'name'
            
        sort_field = getattr(Piece, sort_by, Piece.name)
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())
            
        # Execute query with error handling
        pieces = session.exec(query).all()
        
        # Return template response
        return templates.TemplateResponse(
            "pieces/list_content.html", {"request": request, "pieces": pieces}
        )
        
    except Exception as e:
        # Proper error handling instead of letting exceptions bubble up
        print(f"Error in list_pieces_api: {e}")  # Log for debugging
        
        # Return user-friendly error message
        error_html = f"""
        <div id="piece-list-container" class="card-grid">
            <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                <p>Sorry, there was an error loading piece types.</p>
                <p style="font-size: 0.9em;">Please try refreshing the page or contact support if the problem persists.</p>
            </div>
        </div>
        """
        return HTMLResponse(content=error_html, status_code=200)

@router.post("/api/pieces/", response_class=HTMLResponse)
async def create_piece(
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    active: Optional[str] = Form(None)
):
    """API endpoint to create a new piece."""
    # Convert HTML form data to proper types
    description = description.strip() or None
    active_bool = form_bool(active) if active is not None else True
    
    new_piece = Piece(
        name=name, 
        description=description,
        active=active_bool
    )
    session.add(new_piece)
    session.commit()
    session.refresh(new_piece)

    response = RedirectResponse(url=f"/pieces/{new_piece.piecid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/pieces/{new_piece.piecid}" 
    return response

@router.put("/api/pieces/{piecid}", response_class=HTMLResponse)
async def update_piece(
    piecid: int,
    request: Request,
    session: Session = Depends(get_session),
    name: str = Form(...),
    description: str = Form(""),
    active: Optional[str] = Form(None)
):
    """API endpoint to update an existing piece."""
    
    piece = session.get(Piece, piecid)
    if not piece:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece not found")

    # Convert HTML form data to proper types
    description = description.strip() or None
    active_bool = form_bool(active) if active is not None else piece.active

    piece.name = name
    piece.description = description
    piece.active = active_bool

    session.add(piece)
    session.commit()
    session.refresh(piece)

    response = RedirectResponse(url=f"/pieces/{piece.piecid}", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = f"/pieces/{piece.piecid}"
    return response

@router.delete("/api/pieces/{piecid}")
async def delete_piece(piecid: int, session: Session = Depends(get_session)):
    """API endpoint to soft delete a piece."""
    piece_to_delete = session.get(Piece, piecid)
    if not piece_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Piece not found")

    # Check if piece is used by any components
    linked_components = session.exec(select(Component).where(Component.pieceid == piecid, Component.active == True)).all()
    
    if linked_components:
        # Don't delete if components are using this piece
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Cannot delete piece type. {len(linked_components)} active components are using this piece type."
        )

    piece_to_delete.active = False
    session.add(piece_to_delete)
    session.commit()

    response = HTMLResponse(content="", status_code=status.HTTP_204_NO_CONTENT)
    response.headers["HX-Redirect"] = "/pieces/" 
    return response

@router.get("/api/pieces/{piecid}/components", response_class=HTMLResponse)
async def get_components_by_piece(piecid: int, request: Request, session: Session = Depends(get_session)):
    """HTMX endpoint to list components using a specific piece type."""
    piece = session.get(Piece, piecid)
    if not piece:
        return HTMLResponse("<p class='text-center text-secondary'>Piece type not found.</p>")

    components = session.exec(
        select(Component)
        .where(Component.pieceid == piecid, Component.active == True)
        .order_by(Component.name)
    ).all()

    if components:
        return templates.TemplateResponse(
            "components/list_content.html", 
            {"request": request, "components": components}
        )
    else:
        return HTMLResponse("<p class='text-center text-secondary'>No active components found for this piece type.</p>")