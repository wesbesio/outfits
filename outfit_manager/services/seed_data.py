# File: services/seed_data.py
# Revision: 1.0 - Initial data creation

from sqlmodel import Session
from models import Vendor, Piece
from models.database import engine

def create_initial_vendors():
    """Create initial vendor data."""
    vendors = [
        {"name": "Amazon", "description": "Online marketplace"},
        {"name": "Poshmark", "description": "Social commerce marketplace"},
        {"name": "Nordstrom", "description": "Upscale department store"},
        {"name": "Target", "description": "Discount retail store"},
        {"name": "Zara", "description": "Fast fashion retailer"},
        {"name": "H&M", "description": "Swedish fashion retailer"},
        {"name": "Uniqlo", "description": "Japanese casual wear designer"},
        {"name": "Local Store", "description": "Physical retail store"}
    ]
    
    with Session(engine) as session:
        for vendor_data in vendors:
            vendor = Vendor(**vendor_data)
            session.add(vendor)
        session.commit()

def create_initial_pieces():
    """Create initial piece type data."""
    pieces = [
        {"name": "Shirt", "description": "Tops, blouses, t-shirts"},
        {"name": "Pants", "description": "Trousers, jeans, leggings"},
        {"name": "Dress", "description": "One-piece garments"},
        {"name": "Skirt", "description": "Lower body garments"},
        {"name": "Jacket", "description": "Outerwear, blazers, coats"},
        {"name": "Shoes", "description": "Footwear"},
        {"name": "Accessories", "description": "Jewelry, bags, belts"},
        {"name": "Undergarments", "description": "Underwear, bras, shapewear"},
        {"name": "Swimwear", "description": "Bathing suits, bikinis"},
        {"name": "Activewear", "description": "Athletic and workout clothing"}
    ]
    
    with Session(engine) as session:
        for piece_data in pieces:
            piece = Piece(**piece_data)
            session.add(piece)
        session.commit()

def seed_database():
    """Seed database with initial data."""
    print("🌱 Seeding database with initial data...")
    
    create_initial_vendors()
    print("✅ Created initial vendors")
    
    create_initial_pieces()
    print("✅ Created initial piece types")
    
    print("🎉 Database seeding complete!")

if __name__ == "__main__":
    seed_database()
