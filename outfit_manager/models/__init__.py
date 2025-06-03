# File: models/__init__.py
# Revision: 1.0 - SQLModel definitions

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Vendor(SQLModel, table=True):
    """Vendor model for shopping sources."""
    venid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="vendor")
    outfits: List["Outfit"] = Relationship(back_populates="vendor")

class Piece(SQLModel, table=True):
    """Piece model for clothing categories."""
    piecid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    active: bool = Field(default=True)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="piece")

class Component(SQLModel, table=True):
    """Component model for individual clothing items."""
    comid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    brand: Optional[str] = Field(default=None, max_length=100)
    cost: int = Field(default=0)  # Cost in cents
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    vendorid: Optional[int] = Field(default=None, foreign_key="vendor.venid")
    piecid: Optional[int] = Field(default=None, foreign_key="piece.piecid")
    image: Optional[bytes] = Field(default=None)  # BLOB storage
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    vendor: Optional[Vendor] = Relationship(back_populates="components")
    piece: Optional[Piece] = Relationship(back_populates="components")
    outfit_links: List["Out2Comp"] = Relationship(back_populates="component")

class Outfit(SQLModel, table=True):
    """Outfit model for collections of components."""
    outid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    totalcost: int = Field(default=0)  # Total cost in cents
    vendorid: Optional[int] = Field(default=None, foreign_key="vendor.venid")
    image: Optional[bytes] = Field(default=None)  # BLOB storage
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    vendor: Optional[Vendor] = Relationship(back_populates="outfits")
    component_links: List["Out2Comp"] = Relationship(back_populates="outfit")

class Out2Comp(SQLModel, table=True):
    """Many-to-many relationship between outfits and components."""
    o2cid: Optional[int] = Field(default=None, primary_key=True)
    outid: int = Field(foreign_key="outfit.outid")
    comid: int = Field(foreign_key="component.comid")
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    outfit: Outfit = Relationship(back_populates="component_links")
    component: Component = Relationship(back_populates="outfit_links")
