from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# Base Models
class VendorBase(SQLModel):
    name: str
    description: Optional[str] = None
    active: bool = True
    flag: bool = False

class Vendor(VendorBase, table=True):
    __tablename__ = "vendors"
    
    venid: Optional[int] = Field(default=None, primary_key=True)
    creation: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="vendor")

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    flag: Optional[bool] = None

# Pieces Model
class PieceBase(SQLModel):
    name: str
    description: Optional[str] = None
    active: bool = True

class Piece(PieceBase, table=True):
    __tablename__ = "pieces"
    
    piecid: Optional[int] = Field(default=None, primary_key=True)
    creation: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="piece")

class PieceCreate(PieceBase):
    pass

# Component Models
class ComponentBase(SQLModel):
    name: str
    description: Optional[str] = None
    brand: Optional[str] = None
    cost: int = 0
    notes: Optional[str] = None
    active: bool = True
    flag: bool = False

class Component(ComponentBase, table=True):
    __tablename__ = "components"
    
    comid: Optional[int] = Field(default=None, primary_key=True)
    vendorid: Optional[int] = Field(default=None, foreign_key="vendors.venid")
    piecid: Optional[int] = Field(default=None, foreign_key="pieces.piecid")
    creation: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    image: Optional[bytes] = None
    
    # Relationships
    vendor: Optional[Vendor] = Relationship(back_populates="components")
    piece: Optional[Piece] = Relationship(back_populates="components")
    outfit_links: List["Out2Comp"] = Relationship(back_populates="component")

class ComponentCreate(ComponentBase):
    vendorid: Optional[int] = None
    piecid: Optional[int] = None

class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    cost: Optional[int] = None
    notes: Optional[str] = None
    vendorid: Optional[int] = None
    piecid: Optional[int] = None
    active: Optional[bool] = None
    flag: Optional[bool] = None

# Outfit Models
class OutfitBase(SQLModel):
    name: str
    description: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True
    flag: bool = False

class Outfit(OutfitBase, table=True):
    __tablename__ = "outfit"
    
    outid: Optional[int] = Field(default=None, primary_key=True)
    totalcost: int = 0
    vendorid: Optional[int] = Field(default=None, foreign_key="vendors.venid")
    creation: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    image: Optional[bytes] = None
    
    # Relationships
    component_links: List["Out2Comp"] = Relationship(back_populates="outfit")

class OutfitCreate(OutfitBase):
    vendorid: Optional[int] = None

class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    vendorid: Optional[int] = None
    active: Optional[bool] = None
    flag: Optional[bool] = None

# Junction Table for Many-to-Many
class Out2Comp(SQLModel, table=True):
    __tablename__ = "out2comp"
    
    o2cid: Optional[int] = Field(default=None, primary_key=True)
    outid: Optional[int] = Field(default=None, foreign_key="outfit.outid")
    comid: Optional[int] = Field(default=None, foreign_key="components.comid")
    active: bool = True
    flag: bool = False
    creation: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    
    # Relationships
    outfit: Optional[Outfit] = Relationship(back_populates="component_links")
    component: Optional[Component] = Relationship(back_populates="outfit_links")

# Response Models with calculated fields
class ComponentResponse(ComponentBase):
    comid: int
    vendorid: Optional[int] = None
    piecid: Optional[int] = None
    creation: datetime
    modified: datetime
    has_image: bool = False
    vendor_name: Optional[str] = None
    piece_name: Optional[str] = None

class OutfitResponse(OutfitBase):
    outid: int
    totalcost: int
    vendorid: Optional[int] = None
    creation: datetime
    modified: datetime
    has_image: bool = False
    calculated_cost: int = 0
    component_count: int = 0