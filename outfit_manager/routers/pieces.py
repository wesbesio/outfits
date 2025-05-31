from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from models.database import get_session
from models import Piece, PieceCreate

router = APIRouter()

@router.get("/", response_model=List[Piece])
async def get_pieces(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    """Get list of piece types"""
    query = select(Piece)
    
    if active_only:
        query = query.where(Piece.active == True)
    
    query = query.offset(skip).limit(limit)
    pieces = session.exec(query).all()
    
    return pieces

@router.get("/{piece_id}", response_model=Piece)
async def get_piece(piece_id: int, session: Session = Depends(get_session)):
    """Get single piece by ID"""
    piece = session.get(Piece, piece_id)
    if not piece:
        raise HTTPException(status_code=404, detail="Piece type not found")
    
    return piece

@router.post("/", response_model=Piece)
async def create_piece(piece: PieceCreate, session: Session = Depends(get_session)):
    """Create new piece type"""
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
    
    return db_piece