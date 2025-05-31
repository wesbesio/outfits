from sqlmodel import Session, select
from models import Vendor, Piece

def create_seed_data(session: Session):
    """Create initial seed data for vendors and pieces"""
    
    # Seed vendors
    vendor_names = ["ebay", "Poshmark", "ThredUP", "Amazon"]
    
    for vendor_name in vendor_names:
        # Check if vendor already exists
        existing_vendor = session.exec(
            select(Vendor).where(Vendor.name == vendor_name)
        ).first()
        
        if not existing_vendor:
            vendor = Vendor(
                name=vendor_name,
                description=f"Items from {vendor_name}",
                active=True
            )
            session.add(vendor)
    
    # Seed piece types
    piece_types = [
        "Headwear", "Outerwear", "Dress", "Pants", "Shorts", 
        "Sweater", "Shirt", "Shoes", "Accessories"
    ]
    
    for piece_name in piece_types:
        # Check if piece already exists
        existing_piece = session.exec(
            select(Piece).where(Piece.name == piece_name)
        ).first()
        
        if not existing_piece:
            piece = Piece(
                name=piece_name,
                description=f"{piece_name} clothing items",
                active=True
            )
            session.add(piece)
    
    # Commit all changes
    session.commit()
    print("Seed data created successfully!")