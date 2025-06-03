# File: services/seed_data.py
# Revision: 1.0 - Initial data creation

from sqlmodel import Session
from models import Vendor, Piece
from models.database import engine

def seed_initial_data(session: Session):
    """Seeds the database with initial Vendor and Piece data."""
    vendors = [
        Vendor(name="Amazon", description="Online retail giant"),
        Vendor(name="Poshmark", description="Social marketplace for new and used style"),
        Vendor(name="Zara", description="Fast fashion retailer"),
        Vendor(name="Nike", description="Athletic apparel and footwear"),
    ]

    pieces = [
        Piece(name="Shirt", description="Upper body garment"),
        Piece(name="Pants", description="Lower body garment"),
        Piece(name="Shoes", description="Footwear"),
        Piece(name="Jacket", description="Outerwear"),
        Piece(name="Accessory", description="Additional item like a belt or jewelry"),
    ]

    # Check if data already exists to prevent duplicates
    if session.query(Vendor).first() is None:
        session.add_all(vendors)
        print("Seeding initial vendors...")
    else:
        print("Vendors already exist, skipping seeding.")

    if session.query(Piece).first() is None:
        session.add_all(pieces)
        print("Seeding initial pieces...")
    else:
        print("Pieces already exist, skipping seeding.")

    session.commit()
    print("Initial data seeding complete.")

if __name__ == "__main__":
    # This block is for running the seed script directly for testing
    from models.database import create_db_and_tables
    print("Creating database and tables before seeding...")
    create_db_and_tables()
    with Session(engine) as session:
        seed_initial_data(session)