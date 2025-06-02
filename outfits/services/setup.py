# File: setup.py
# Revision: 1.0 - Create complete outfit manager project structure

import os
from pathlib import Path

def create_directory_structure():
    """Create all required directories"""
    
    directories = [
        "models",
        "routers", 
        "services",
        "templates",
        "templates/forms",
        "templates/outfits",
        "templates/components", 
        "templates/partials",
        "static",
        "static/css",
        "static/js"
    ]
    
    print("📁 Creating directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}/")

def create_python_files():
    """Create all Python files with starter content"""
    
    print("\n🐍 Creating Python files...")
    
    # main.py
    main_py_content = '''# File: main.py
# Revision: 1.0 - FastAPI app with web routes and HTMX support

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from models.database import create_db_and_tables, get_session
from sqlmodel import Session, select
from models import Outfit, Component, Vendor, Piece
from services.seed_data import create_seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    # Create seed data
    session = next(get_session())
    create_seed_data(session)
    session.close()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Outfit Manager",
    description="Fashion outfit and component management system with HTMX frontend",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include API routers
from routers import outfits, components, vendors, images, pieces

app.include_router(outfits.router, prefix="/api/outfits", tags=["outfits"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(pieces.router, prefix="/api/pieces", tags=["pieces"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

# HOME PAGE
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

# OUTFITS LIST
@app.get("/outfits", response_class=HTMLResponse)
async def outfits_list(request: Request):
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "outfits/list_content.html" if is_htmx else "outfits/list.html"
    return templates.TemplateResponse(template, {"request": request})

# COMPONENTS LIST
@app.get("/components", response_class=HTMLResponse)
async def components_list(request: Request):
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "components/list_content.html" if is_htmx else "components/list.html"
    return templates.TemplateResponse(template, {"request": request})

# NEW COMPONENT FORM
@app.get("/new-component", response_class=HTMLResponse)
async def new_component_form(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    pieces = session.exec(select(Piece).where(Piece.active == True)).all()
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "forms/component_form_content.html" if is_htmx else "forms/component_form.html"
    
    return templates.TemplateResponse(template, {
        "request": request,
        "component": None,
        "vendors": vendors,
        "pieces": pieces,
        "is_edit": False,
        "page_title": "Create New Component"
    })

# NEW OUTFIT FORM
@app.get("/outfits/new", response_class=HTMLResponse)
async def new_outfit_form(request: Request, session: Session = Depends(get_session)):
    vendors = session.exec(select(Vendor).where(Vendor.active == True)).all()
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "forms/outfit_form_content.html" if is_htmx else "forms/outfit_form.html"
    
    return templates.TemplateResponse(template, {
        "request": request,
        "outfit": None,
        "vendors": vendors,
        "is_edit": False,
        "page_title": "Create New Outfit"
    })

# NEW VENDOR FORM
@app.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor_form(request: Request):
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "forms/vendor_form_content.html" if is_htmx else "forms/vendor_form.html"
    
    return templates.TemplateResponse(template, {
        "request": request,
        "vendor": None,
        "is_edit": False,
        "page_title": "Create New Vendor"
    })

# COMPONENT DETAIL
@app.get("/components/{component_id}", response_class=HTMLResponse)
async def component_detail(request: Request, component_id: int, session: Session = Depends(get_session)):
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    is_htmx = request.headers.get('HX-Request') == 'true'
    template = "components/detail_content.html" if is_htmx else "components/detail.html"
    
    return templates.TemplateResponse(template, {
        "request": request,
        "component": component
    })

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
    
    # models/__init__.py
    models_init_content = '''# File: models/__init__.py
# Revision: 1.0 - Complete SQLModel definitions for outfit management

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
'''
    
    # models/database.py
    database_content = '''# File: models/database.py
# Revision: 1.0 - Database configuration and session management

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database URL - use SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./outfit_manager.db")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database and tables"""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Database session dependency"""
    with Session(engine) as session:
        yield session
'''
    
    # requirements.txt
    requirements_content = '''fastapi==0.104.1
sqlmodel==0.0.14
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pillow==10.1.0
jinja2==3.1.2
python-dotenv==1.0.0
'''
    
    # Create all Python files
    files_to_create = [
        ("main.py", main_py_content),
        ("models/__init__.py", models_init_content),
        ("models/database.py", database_content),
        ("requirements.txt", requirements_content),
    ]
    
    for file_path, content in files_to_create:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    # Create empty __init__.py files for packages
    init_files = [
        "routers/__init__.py",
        "services/__init__.py"
    ]
    
    for init_file in init_files:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'# File: {init_file}\n# Revision: 1.0 - Package initialization\n')
        print(f"✅ Created: {init_file}")

def create_router_files():
    """Create all router files with starter content"""
    
    print("\n🛣️ Creating router files...")
    
    # routers/components.py
    components_router_content = '''# File: routers/components.py
# Revision: 1.0 - Component CRUD operations with HTMX support

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime

from models.database import get_session
from models import (
    Component, ComponentCreate, ComponentUpdate, ComponentResponse,
    Vendor, Piece, Outfit, Out2Comp
)
from services.image_service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=Union[List[ComponentResponse], HTMLResponse])
async def get_components(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    sort_by: str = "name",
    filter_vendor: Optional[int] = None,
    filter_piece: Optional[int] = None,
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of components with optional filtering and sorting"""
    
    query = select(Component)
    
    # Apply filters
    if active_only:
        query = query.where(Component.active == True)
    
    if filter_vendor:
        query = query.where(Component.vendorid == filter_vendor)
    
    if filter_piece:
        query = query.where(Component.piecid == filter_piece)
    
    # Apply sorting
    if sort_by == "cost":
        query = query.order_by(Component.cost.desc())
    elif sort_by == "brand":
        query = query.order_by(Component.brand)
    elif sort_by == "created":
        query = query.order_by(Component.creation.desc())
    elif sort_by == "modified":
        query = query.order_by(Component.modified.desc())
    else:  # Default to name
        query = query.order_by(Component.name)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    components = session.exec(query).all()
    
    # Prepare component responses with additional data
    component_responses = []
    for component in components:
        component_response = ComponentResponse(
            **component.model_dump(),
            has_image=component.image is not None,
            vendor_name=component.vendor.name if component.vendor else None,
            piece_name=component.piece.name if component.piece else None
        )
        component_responses.append(component_response)
    
    # Determine if we need to return HTML or JSON
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    
    if is_htmx_request or wants_html:
        # Return HTML content from template
        content = templates.get_template("partials/component_cards.html").render({
            "request": request, 
            "components": component_responses
        })
        return HTMLResponse(content=content)
    else:
        # Return JSON response
        return component_responses

@router.post("/")
async def create_component(
    request: Request,
    name: str = Form(...),
    active: bool = Form(True),
    flag: bool = Form(False),
    description: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    cost: int = Form(0),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    piecid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Create new component with optional image"""
    
    # Create component data
    component_data = {
        "name": name,
        "active": active,
        "flag": flag,
        "description": description,
        "brand": brand,
        "cost": cost,
        "notes": notes,
        "vendorid": vendorid,
        "piecid": piecid
    }
    
    # Create the component
    db_component = Component(**component_data)
    session.add(db_component)
    session.commit()
    session.refresh(db_component)
    
    # Process image if provided
    if file and file.filename:
        try:
            processed_image = await ImageService.validate_and_process_image(file)
            db_component.image = processed_image
            db_component.modified = datetime.now()
            session.add(db_component)
            session.commit()
        except Exception as img_error:
            # Log the error but continue - component was created successfully
            print(f"Error processing image: {str(img_error)}")
    
    # Return HTMX redirect to components list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/components"
    return response

@router.get("/{component_id}/outfits", response_class=HTMLResponse)
async def get_component_outfits(
    request: Request,
    component_id: int,
    session: Session = Depends(get_session)
):
    """Get outfits that use this component as HTML"""
    
    # Check if component exists
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Get outfits that include this component
    outfits_query = select(Outfit).join(Out2Comp).where(
        Out2Comp.comid == component_id,
        Out2Comp.active == True
    )
    outfits = session.exec(outfits_query).all()
    
    # Return HTML partial
    if not outfits:
        return HTMLResponse("""
        <div class="empty-state smaller">
            <div class="empty-content">
                <span class="empty-icon">👗</span>
                <h3>Not used in any outfits</h3>
                <p>This component isn't part of any outfits yet.</p>
            </div>
        </div>
        """)
    
    # Return outfit cards
    html = '<div class="outfit-cards">'
    for outfit in outfits:
        html += f'''
    <div class="outfit-card-mini" 
            hx-get="/outfits/{outfit.outid}" 
            hx-target="#main-content" 
            hx-push-url="true">
        <div class="outfit-card-image">
            {f'<img src="/api/images/outfit/{outfit.outid}?thumbnail=true" alt="{outfit.name}" loading="lazy">' if outfit.image else '<div class="card-image-placeholder mini">👗</div>'}
        </div>
        <div class="outfit-card-content">
            <h4 class="outfit-card-title">{outfit.name}</h4>
            <span class="outfit-card-cost">${outfit.totalcost}</span>
        </div>
    </div>
        '''
    html += '</div>'
    
    return HTMLResponse(content=html)
'''
    
    # routers/outfits.py
    outfits_router_content = '''# File: routers/outfits.py
# Revision: 1.0 - Outfit CRUD operations with HTMX support

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Header
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import List, Optional, Union
from datetime import datetime

from models.database import get_session
from models import (
    Outfit, OutfitCreate, OutfitUpdate, OutfitResponse,
    Out2Comp, Component
)
from services.image_service import ImageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get_outfits(
    request: Request = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    sort_by: str = "name",
    accept: Optional[str] = Header(None),
    session: Session = Depends(get_session)
):
    """Get list of outfits with optional filtering and sorting"""
    
    query = select(Outfit)
    
    # Apply filters
    if active_only:
        query = query.where(Outfit.active == True)
    
    # Apply sorting
    if sort_by == "cost":
        query = query.order_by(Outfit.totalcost.desc())
    elif sort_by == "created":
        query = query.order_by(Outfit.creation.desc())
    elif sort_by == "modified":
        query = query.order_by(Outfit.modified.desc())
    else:  # Default to name
        query = query.order_by(Outfit.name)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    outfits = session.exec(query).all()
    
    # Enhanced outfit responses with calculated costs and component counts
    outfit_responses = []
    for outfit in outfits:
        # Get components for this outfit
        components_query = select(Component).join(Out2Comp).where(
            Out2Comp.outid == outfit.outid,
            Out2Comp.active == True
        )
        components = session.exec(components_query).all()
        
        # Calculate total cost of components
        calculated_cost = sum(comp.cost for comp in components)
        
        # Format creation date
        creation_formatted = outfit.creation.strftime("%b %d, %Y") if outfit.creation else None
        
        outfit_response = OutfitResponse(
            **outfit.model_dump(),
            has_image=outfit.image is not None,
            calculated_cost=calculated_cost,
            component_count=len(components),
        )
        outfit_response.creation_formatted = creation_formatted
        outfit_responses.append(outfit_response)
    
    # Determine if we need to return HTML or JSON
    is_htmx_request = request and request.headers.get("HX-Request") == "true"
    wants_html = accept and "text/html" in accept
    
    if is_htmx_request or wants_html:
        # Return HTML content from template
        content = templates.get_template("partials/outfit_cards.html").render({
            "request": request, 
            "outfits": outfit_responses
        })
        return HTMLResponse(content=content)
    
    return outfit_responses

@router.post("/")
async def create_outfit(
    request: Request,
    name: str = Form(...),
    active: bool = Form(True),
    flag: bool = Form(False),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    """Create new outfit with optional image"""
    
    # Create outfit data
    outfit_data = {
        "name": name,
        "active": active,
        "flag": flag,
        "description": description,
        "notes": notes,
        "vendorid": vendorid,
        "totalcost": 0  # Will be calculated later
    }
    
    # Create the outfit
    db_outfit = Outfit(**outfit_data)
    session.add(db_outfit)
    session.commit()
    session.refresh(db_outfit)
    
    # Process image if provided
    if file and file.filename:
        try:
            processed_image = await ImageService.validate_and_process_image(file)
            db_outfit.image = processed_image
            db_outfit.modified = datetime.now()
            session.add(db_outfit)
            session.commit()
        except Exception as img_error:
            # Log the error but continue - outfit was created successfully
            print(f"Error processing image: {str(img_error)}")
    
    # Return HTMX redirect to outfits list
    response = Response(status_code=200)
    response.headers["HX-Redirect"] = "/outfits"
    return response
'''
    
    # Create other router files with basic structure
    router_files = [
        ("routers/components.py", components_router_content),
        ("routers/outfits.py", outfits_router_content),
        ("routers/vendors.py", '''# File: routers/vendors.py
# Revision: 1.0 - Vendor management endpoints

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
'''),
        ("routers/pieces.py", '''# File: routers/pieces.py
# Revision: 1.0 - Piece type management endpoints

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
'''),
        ("routers/images.py", '''# File: routers/images.py
# Revision: 1.0 - Image serving endpoints

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlmodel import Session
from typing import Optional

from models.database import get_session
from models import Component, Outfit
from services.image_service import ImageService

router = APIRouter()

@router.get("/component/{component_id}")
async def get_component_image(
    component_id: int,
    thumbnail: bool = False,
    session: Session = Depends(get_session)
):
    """Serve component image"""
    component = session.get(Component, component_id)
    
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    if not component.image:
        raise HTTPException(status_code=404, detail="No image found for this component")
    
    image_data = component.image
    
    # Create thumbnail if requested
    if thumbnail:
        image_data = ImageService.create_thumbnail(image_data)
    
    return Response(
        content=image_data,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f"inline; filename=component_{component_id}.jpg"
        }
    )

@router.get("/outfit/{outfit_id}")
async def get_outfit_image(
    outfit_id: int,
    thumbnail: bool = False,
    session: Session = Depends(get_session)
):
    """Serve outfit image"""
    outfit = session.get(Outfit, outfit_id)
    
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    if not outfit.image:
        raise HTTPException(status_code=404, detail="No image found for this outfit")
    
    image_data = outfit.image
    
    # Create thumbnail if requested
    if thumbnail:
        image_data = ImageService.create_thumbnail(image_data)
    
    return Response(
        content=image_data,
        media_type="image/jpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f"inline; filename=outfit_{outfit_id}.jpg"
        }
    )
''')
    ]
    
    for file_path, content in router_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")

def create_service_files():
    """Create service files with starter content"""
    
    print("\n🔧 Creating service files...")
    
    # services/image_service.py
    image_service_content = '''# File: services/image_service.py
# Revision: 1.0 - Image processing and validation service

from PIL import Image
import io
from fastapi import HTTPException, UploadFile
from typing import Optional

class ImageService:
    # Allowed image formats
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_SIZE = (1200, 1200)  # Max dimensions
    THUMBNAIL_SIZE = (300, 300)  # Thumbnail dimensions
    QUALITY = 85  # JPEG quality

    @classmethod
    async def validate_and_process_image(cls, file: UploadFile) -> bytes:
        """Validate and process uploaded image file"""
        
        # Check file size
        contents = await file.read()
        if len(contents) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        try:
            # Open and validate image
            image = Image.open(io.BytesIO(contents))
            
            # Check format
            if image.format not in cls.ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported image format. Allowed formats: {', '.join(cls.ALLOWED_FORMATS)}"
                )
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > cls.MAX_IMAGE_SIZE[0] or image.size[1] > cls.MAX_IMAGE_SIZE[1]:
                image.thumbnail(cls.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Save processed image to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=cls.QUALITY, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=400,
                detail="Invalid image file or processing error"
            )

    @classmethod
    def create_thumbnail(cls, image_data: bytes) -> bytes:
        """Create thumbnail from image data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create thumbnail
            image.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=cls.QUALITY, optimize=True)
            
            return output.getvalue()
            
        except Exception:
            # Return original if thumbnail creation fails
            return image_data
'''
    
    # services/seed_data.py
    seed_data_content = '''# File: services/seed_data.py
# Revision: 1.0 - Initial seed data for vendors and pieces

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
'''
    
    service_files = [
        ("services/image_service.py", image_service_content),
        ("services/seed_data.py", seed_data_content)
    ]
    
    for file_path, content in service_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")

def create_static_files():
    """Create CSS and JavaScript files"""
    
    print("\n🎨 Creating static files...")
    
    # static/css/main.css
    main_css_content = '''/* File: static/css/main.css
   Revision: 1.0 - Complete design system with purple theme and HTMX support
*/

/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    /* Purple Theme Colors */
    --primary-color: #8B5CF6;
    --primary-dark: #7C3AED;
    --primary-light: #A78BFA;
    --secondary-color: #EC4899;
    --accent-color: #F3E8FF;
    
    /* Neutral Colors */
    --bg-color: #FAFAFA;
    --bg-gradient: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 50%, #F0F4FF 100%);
    --card-bg: rgba(255, 255, 255, 0.9);
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --text-muted: #9CA3AF;
    
    /* Status Colors */
    --success-color: #10B981;
    --error-color: #EF4444;
    --warning-color: #F59E0B;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 300ms ease-in-out;
    --transition-slow: 500ms ease-in-out;
}

/* Body and Layout */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: var(--bg-gradient);
    color: var(--text-primary);
    line-height: 1.6;
    min-height: 100vh;
    padding-bottom: 80px; /* Space for bottom nav */
}

.bg-gradient {
    background: var(--bg-gradient);
    background-attachment: fixed;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

/* Header */
.header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-md);
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
}

.header .container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--spacing-md);
}

.header-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}

.icon {
    font-size: 1.25em;
}

/* Main Navigation */
.main-nav {
    display: flex;
    gap: var(--spacing-sm);
}

.nav-btn {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-lg);
    text-decoration: none;
    color: var(--text-secondary);
    font-weight: 500;
    transition: all var(--transition-fast);
    border: 2px solid transparent;
}

.nav-btn:hover {
    background: var(--accent-color);
    color: var(--primary-color);
    transform: translateY(-1px);
}

.nav-btn.active {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-dark);
}

.nav-icon {
    font-size: 1.1em;
}

/* Main Content */
.main-content {
    min-height: calc(100vh - 140px);
    padding: var(--spacing-lg) 0;
    transition: opacity 300ms ease-in-out;
}

.main-content.htmx-swapping {
    opacity: 0.5;
}

/* Welcome Screen */
.welcome-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
}

.welcome-content h2 {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}

.welcome-content p {
    font-size: 1.125rem;
    color: var(--text-secondary);
    margin-bottom: var(--spacing-xl);
}

.quick-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    flex-wrap: wrap;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--radius-md);
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all var(--transition-fast);
    font-size: 0.875rem;
    white-space: nowrap;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
    box-shadow: var(--shadow-md);
}

.btn-primary:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background: white;
    color: var(--primary-color);
    border: 2px solid var(--primary-color);
    box-shadow: var(--shadow-sm);
}

.btn-secondary:hover {
    background: var(--primary-color);
    color: white;
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.btn-large {
    padding: var(--spacing-md) var(--spacing-xl);
    font-size: 1rem;
}

.btn-small {
    padding: var(--spacing-xs) var(--spacing-sm);
    font-size: 0.75rem;
}

/* Cards */
.card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: var(--spacing-lg);
    padding: var(--spacing-md);
}

.card {
    background: var(--card-bg);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    transition: all var(--transition-normal);
    border: 1px solid rgba(139, 92, 246, 0.1);
    cursor: pointer;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-xl);
    border-color: var(--primary-color);
}

.card-image {
    width: 100%;
    height: 200px;
    background: linear-gradient(135deg, var(--accent-color) 0%, #E0E7FF 100%);
    position: relative;
    overflow: hidden;
}

.card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform var(--transition-normal);
}

.card:hover .card-image img {
    transform: scale(1.05);
}

.card-image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    color: var(--primary-light);
    background: linear-gradient(135deg, var(--accent-color) 0%, #E0E7FF 100%);
}

.card-content {
    padding: var(--spacing-lg);
}

.card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
    line-height: 1.2;
}

.card-subtitle {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: var(--spacing-md);
}

.card-description {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.5;
    margin-bottom: var(--spacing-md);
}

.card-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-md);
    padding-top: var(--spacing-md);
    border-top: 1px solid rgba(139, 92, 246, 0.1);
}

.card-price {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--primary-color);
}

.card-badge {
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-md);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

.badge-active {
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.badge-inactive {
    background: rgba(107, 114, 128, 0.1);
    color: var(--text-muted);
}

/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-around;
    padding: var(--spacing-sm) var(--spacing-md);
    border-top: 1px solid rgba(139, 92, 246, 0.1);
}

.bottom-nav-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm);
    background: none;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
    border-radius: var(--radius-md);
    min-width: 60px;
    text-decoration: none;
}

.bottom-nav-btn:hover {
    background: var(--accent-color);
    color: var(--primary-color);
    transform: translateY(-2px);
}

.bottom-nav-icon {
    font-size: 1.25rem;
}

.bottom-nav-label {
    font-size: 0.75rem;
    font-weight: 500;
}

/* Forms */
.form {
    padding: var(--spacing-xl);
}

.form-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: var(--spacing-lg);
    text-align: center;
}

.form-group {
    margin-bottom: var(--spacing-lg);
}

.form-label {
    display: block;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
}

.form-input,
.form-select,
.form-textarea {
    width: 100%;
    padding: var(--spacing-md);
    border: 2px solid #E5E7EB;
    border-radius: var(--radius-md);
    font-size: 0.875rem;
    transition: border-color var(--transition-fast);
    background: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.form-textarea {
    resize: vertical;
    min-height: 80px;
}

.form-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    margin-top: var(--spacing-xl);
    padding-top: var(--spacing-lg);
    border-top: 1px solid #E5E7EB;
}

/* Radio Buttons */
.radio-group {
    display: flex;
    gap: var(--spacing-md);
}

.radio-option {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: 2px solid #E5E7EB;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-fast);
}

.radio-option:hover {
    border-color: var(--primary-light);
}

.radio-option.selected {
    border-color: var(--primary-color);
    background: var(--accent-color);
}

.radio-option input[type="radio"] {
    display: none;
}

/* Empty State */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-2xl);
    text-align: center;
    min-height: 300px;
    background: rgba(255, 255, 255, 0.7);
    border-radius: var(--radius-lg);
    margin: var(--spacing-xl) 0;
    box-shadow: var(--shadow-md);
}

.empty-content {
    max-width: 400px;
}

.empty-icon {
    font-size: 4rem;
    color: var(--primary-light);
    margin-bottom: var(--spacing-lg);
    display: block;
}

.empty-content h3 {
    color: var(--text-primary);
    margin-bottom: var(--spacing-sm);
    font-size: 1.5rem;
    font-weight: 700;
}

.empty-content p {
    color: var(--text-secondary);
    margin-bottom: var(--spacing-lg);
    font-size: 1.1rem;
}

/* HTMX Indicator */
.htmx-indicator {
    opacity: 0;
    transition: opacity 300ms ease-in;
}

.htmx-request .htmx-indicator {
    opacity: 1;
}

.htmx-request.htmx-indicator {
    opacity: 1;
}

/* Loading States */
.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-2xl);
    color: var(--text-secondary);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(139, 92, 246, 0.1);
    border-left: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--spacing-sm);
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Form Page Styles */
.form-page {
    background: white;
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-lg);
    max-width: 600px;
    margin: 0 auto;
    overflow: hidden;
}

.form-page-header {
    background: var(--accent-color);
    padding: var(--spacing-xl);
    text-align: center;
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
}

.form-page-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: var(--spacing-sm);
}

.form-page-subtitle {
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.breadcrumb-nav {
    margin-bottom: var(--spacing-lg);
    text-align: center;
}

.breadcrumb-link {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-xs);
    transition: color var(--transition-fast);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    background: rgba(139, 92, 246, 0.1);
}

.breadcrumb-link:hover {
    color: var(--primary-dark);
    background: rgba(139, 92, 246, 0.2);
}

/* Page Header */
.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-xl);
    padding: var(--spacing-lg) 0;
}

.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary-color);
}

.page-actions {
    display: flex;
    gap: var(--spacing-md);
}

/* Controls and Stats */
.controls-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.8);
    padding: var(--spacing-md);
    border-radius: var(--radius-lg);
    margin-bottom: var(--spacing-md);
    box-shadow: var(--shadow-sm);
}

.stats-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
}

.stat-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    text-align: center;
    box-shadow: var(--shadow-sm);
    border: 1px solid rgba(139, 92, 246, 0.1);
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--primary-color);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: 0.875rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.025em;
    font-weight: 600;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header .container {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .main-nav {
        width: 100%;
        justify-content: center;
    }
    
    .nav-btn {
        flex: 1;
        justify-content: center;
    }
    
    .card-grid {
        grid-template-columns: 1fr;
        padding: var(--spacing-sm);
    }
    
    .quick-actions {
        flex-direction: column;
        align-items: center;
    }
    
    .form-actions {
        flex-direction: column;
    }
    
    .radio-group {
        flex-direction: column;
    }
    
    .page-header {
        flex-direction: column;
        gap: var(--spacing-md);
        text-align: center;
    }
    
    .form-page {
        margin: var(--spacing-md);
    }
    
    .controls-bar {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .stats-bar {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.hidden { display: none !important; }
.visible { display: block !important; }

.mt-sm { margin-top: var(--spacing-sm); }
.mt-md { margin-top: var(--spacing-md); }
.mt-lg { margin-top: var(--spacing-lg); }

.mb-sm { margin-bottom: var(--spacing-sm); }
.mb-md { margin-bottom: var(--spacing-md); }
.mb-lg { margin-bottom: var(--spacing-lg); }

.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }
'''
    
    # static/js/main.js
    main_js_content = '''// File: static/js/main.js
// Revision: 1.0 - Minimal utilities for HTMX-focused app

// Better navigation with HTMX transitions
function navigateToPage(url, targetSelector = '#main-content') {
    htmx.ajax('GET', url, {
        target: targetSelector,
        swap: 'innerHTML transition:opacity',
        push: true
    });
}

// Toast notification system
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Global HTMX error handler
document.body.addEventListener('htmx:responseError', function(evt) {
    showToast('Something went wrong. Please try again.', 'error');
});

// Global HTMX success handler for forms
document.body.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.successful && evt.detail.elt.tagName === 'FORM') {
        showToast('Saved successfully!', 'success');
    }
});
'''
    
    # static/js/form-error-handler.js
    form_error_js_content = '''// File: static/js/form-error-handler.js
// Revision: 1.0 - HTMX form error handling and validation

// Add HTMX event handlers for form submissions
document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        const response = evt.detail.xhr;
        
        // Try to parse error details from response
        try {
            let errorDetail = "An unknown error occurred";
            
            if (response.status === 422) {
                // Validation error
                const data = JSON.parse(response.responseText);
                if (data.detail && Array.isArray(data.detail)) {
                    // FastAPI validation error format
                    errorDetail = data.detail.map(err => {
                        return `${err.loc.slice(1).join('.')}: ${err.msg}`;
                    }).join('\\n');
                } else if (data.detail) {
                    errorDetail = data.detail;
                }
            } else if (response.status === 404) {
                errorDetail = "Resource not found";
            } else if (response.status === 500) {
                errorDetail = "Server error. Please try again later.";
            } else {
                // Generic error message
                errorDetail = `Error: ${response.status} ${response.statusText}`;
            }
            
            showFormError(evt.target, errorDetail);
            console.error('Form submission error:', errorDetail);
            
        } catch (e) {
            console.error('Error parsing error response:', e);
            showFormError(evt.target, "An unexpected error occurred");
        }
    });
});

// Display error message in the form
function showFormError(formElement, errorMessage) {
    // Find the closest form
    const form = formElement.closest('form');
    if (!form) return;
    
    // Remove any existing error messages
    const existingError = form.querySelector('.form-error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error element
    const errorEl = document.createElement('div');
    errorEl.className = 'form-error-message';
    errorEl.innerHTML = `
        <div class="error-icon">⚠️</div>
        <div class="error-content">
            <h4>Form Submission Error</h4>
            <p>${errorMessage}</p>
        </div>
        <button type="button" class="error-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    // Insert at the top of the form
    form.insertBefore(errorEl, form.firstChild);
    
    // Scroll to error
    errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
'''
    
    static_files = [
        ("static/css/main.css", main_css_content),
        ("static/js/main.js", main_js_content),
        ("static/js/form-error-handler.js", form_error_js_content)
    ]
    
    for file_path, content in static_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")

def create_template_files():
    """Create all HTML template files"""
    
    print("\n📄 Creating template files...")
    
    # templates/base.html
    base_html_content = '''<!-- File: templates/base.html -->
<!-- Revision: 1.0 - Base template with HTMX integration -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Outfit Manager{% endblock %}</title>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    
    <!-- CSS -->
    <link rel="stylesheet" href="/static/css/main.css">
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gradient">
    <!-- Header -->
    <header class="header">
        <div class="container">
            <h1 class="header-title">
                <span class="icon">👗</span>
                Outfit Manager
            </h1>
            
            <!-- Main Navigation -->
            <nav class="main-nav">
                <a href="/outfits" class="nav-btn" 
                   hx-get="/outfits" 
                   hx-target="#main-content" 
                   hx-push-url="true">
                    <span class="nav-icon">👕</span>
                    Outfits
                </a>
                <a href="/components" class="nav-btn"
                   hx-get="/components" 
                   hx-target="#main-content" 
                   hx-push-url="true">
                    <span class="nav-icon">🧥</span>
                    Components
                </a>
            </nav>
        </div>
    </header>

    <!-- Main Content -->
    <main id="main-content" class="main-content" hx-ext="head-support">
        {% block content %}
        <!-- Default home content -->
        <div class="welcome-screen">
            <div class="welcome-content">
                <h2>Welcome to Outfit Manager</h2>
                <p>Organize your wardrobe and create amazing outfits!</p>
                <div class="quick-actions">
                    <a href="/outfits" class="btn btn-primary btn-large" 
                       hx-get="/outfits" hx-target="#main-content" hx-push-url="true">
                        View Outfits
                    </a>
                    <a href="/components" class="btn btn-secondary btn-large"
                       hx-get="/components" hx-target="#main-content" hx-push-url="true">
                        View Components
                    </a>
                </div>
            </div>
        </div>
        {% endblock %}
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
        <a href="/outfits/new" class="bottom-nav-btn" 
           hx-get="/outfits/new" 
           hx-target="#main-content" 
           hx-push-url="true">
            <span class="bottom-nav-icon">➕</span>
            <span class="bottom-nav-label">Add Outfit</span>
        </a>
        
        <a href="/new-component" class="bottom-nav-btn"
           hx-get="/new-component"
           hx-target="#main-content"
           hx-push-url="true">
            <span class="bottom-nav-icon">🧥</span>
            <span class="bottom-nav-label">Add Component</span>
        </a>
        
        <a href="/vendors/new" class="bottom-nav-btn"
           hx-get="/vendors/new"
           hx-target="#main-content"
           hx-push-url="true">
            <span class="bottom-nav-icon">🏪</span>
            <span class="bottom-nav-label">Add Vendor</span>
        </a>
    </nav>

    <!-- Toast Container -->
    <div id="toast-container" class="toast-container"></div>

    <!-- JavaScript -->
    <script src="/static/js/main.js"></script>
    <script src="/static/js/form-error-handler.js"></script>
    
    <!-- HTMX Event Handlers -->
    <script>
        // Handle HTMX errors
        document.body.addEventListener('htmx:responseError', function(evt) {
            if (window.showToast) {
                showToast('Error: ' + evt.detail.xhr.statusText, 'error');
            }
        });
        
        // Update navigation active states
        document.body.addEventListener('htmx:afterSwap', function(evt) {
            updateNavigation();
        });
        
        // Also handle URL changes from HTMX pushState
        document.body.addEventListener('htmx:pushUrl', function(evt) {
            updateNavigation();
        });
        
        function updateNavigation() {
            // Update active nav states based on current URL
            const navButtons = document.querySelectorAll('.nav-btn');
            navButtons.forEach(btn => btn.classList.remove('active'));
            
            const path = window.location.pathname;
            
            if (path.startsWith('/outfits')) {
                document.querySelector('[href="/outfits"]').classList.add('active');
            } else if (path.startsWith('/components') || path.startsWith('/new-component')) {
                document.querySelector('[href="/components"]').classList.add('active');
            }
        }
        
        // Initialize navigation on page load
        document.addEventListener('DOMContentLoaded', updateNavigation);
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
'''
    
    # Create basic template files that don't require complex content
    template_files = [
        ("templates/base.html", base_html_content),
        ("templates/partials/component_cards.html", '''<!-- File: templates/partials/component_cards.html -->
<!-- Revision: 1.0 - Component cards for grid display -->

<div class="card-grid">
    {% for component in components %}
    <div class="card component-card" 
         hx-get="/components/{{ component.comid }}" 
         hx-target="#main-content" 
         hx-push-url="true">
        
        <div class="card-image">
            {% if component.has_image %}
                <img src="/api/images/component/{{ component.comid }}?thumbnail=true" 
                     alt="{{ component.name }}" 
                     loading="lazy">
            {% else %}
                <div class="card-image-placeholder">🧥</div>
            {% endif %}
        </div>
        
        <div class="card-content">
            <h3 class="card-title">{{ component.name }}</h3>
            
            {% if component.brand %}
            <p class="card-subtitle">{{ component.brand }}</p>
            {% endif %}
            
            <div class="card-meta">
                <span class="card-price">${{ component.cost }}</span>
                <span class="card-badge {{ 'badge-active' if component.active else 'badge-inactive' }}">
                    {{ 'Active' if component.active else 'Retired' }}
                </span>
            </div>
        </div>
    </div>
    {% endfor %}
    
    {% if not components %}
    <div class="empty-state">
        <div class="empty-content">
            <span class="empty-icon">🧥</span>
            <h3>No components found</h3>
            <p>Add your first component to get started!</p>
            <a href="/new-component" class="btn btn-primary"
               hx-get="/new-component" 
               hx-target="#main-content"
               hx-push-url="true">
                Add Component
            </a>
        </div>
    </div>
    {% endif %}
</div>
'''),
        ("templates/partials/outfit_cards.html", '''<!-- File: templates/partials/outfit_cards.html -->
<!-- Revision: 1.0 - Outfit cards for grid display -->

<div class="card-grid">
    {% for outfit in outfits %}
    <div class="card outfit-card" 
         hx-get="/outfits/{{ outfit.outid }}" 
         hx-target="#main-content" 
         hx-push-url="true">
        
        <div class="card-image">
            {% if outfit.has_image %}
                <img src="/api/images/outfit/{{ outfit.outid }}?thumbnail=true" 
                     alt="{{ outfit.name }}" 
                     loading="lazy">
            {% else %}
                <div class="card-image-placeholder">👗</div>
            {% endif %}
        </div>
        
        <div class="card-content">
            <h3 class="card-title">{{ outfit.name }}</h3>
            
            {% if outfit.description %}
            <p class="card-subtitle">{{ outfit.description[:50] }}{% if outfit.description|length > 50 %}...{% endif %}</p>
            {% endif %}
            
            <div class="card-meta">
                <span class="card-price">${{ outfit.calculated_cost }}</span>
                <span class="card-badge {{ 'badge-active' if outfit.active else 'badge-inactive' }}">
                    {{ 'Active' if outfit.active else 'Retired' }}
                </span>
            </div>
        </div>
    </div>
    {% endfor %}
    
    {% if not outfits %}
    <div class="empty-state">
        <div class="empty-content">
            <span class="empty-icon">👗</span>
            <h3>No outfits found</h3>
            <p>Create your first outfit to get started!</p>
            <a href="/outfits/new" class="btn btn-primary" 
               hx-get="/outfits/new" 
               hx-target="#main-content"
               hx-push-url="true">
                Create Outfit
            </a>
        </div>
    </div>
    {% endif %}
</div>
'''),
        ("templates/partials/vendor_options.html", '''<!-- File: templates/partials/vendor_options.html -->
<!-- Revision: 1.0 - Vendor options for select elements -->

<option value="">Select vendor...</option>
{% for vendor in vendors %}
<option value="{{ vendor.venid }}">{{ vendor.name }}</option>
{% endfor %}
'''),
        ("templates/partials/piece_options.html", '''<!-- File: templates/partials/piece_options.html -->
<!-- Revision: 1.0 - Piece options for select elements -->

<option value="">Select piece type...</option>
{% for piece in pieces %}
<option value="{{ piece.piecid }}">{{ piece.name }}</option>
{% endfor %}
''')
    ]
    
    # Create placeholder templates for complex files
    complex_templates = [
        "templates/components/list.html",
        "templates/components/list_content.html", 
        "templates/components/detail.html",
        "templates/components/detail_content.html",
        "templates/outfits/list.html",
        "templates/outfits/list_content.html",
        "templates/outfits/detail.html",
        "templates/outfits/detail_content.html",
        "templates/forms/component_form.html",
        "templates/forms/component_form_content.html",
        "templates/forms/outfit_form.html", 
        "templates/forms/outfit_form_content.html",
        "templates/forms/vendor_form.html",
        "templates/forms/vendor_form_content.html"
    ]
    
    for file_path, content in template_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {file_path}")
    
    # Create placeholder complex templates
    for template_path in complex_templates:
        template_name = template_path.split('/')[-1].replace('.html', '')
        template_type = "Full page" if "_content" not in template_path else "HTMX content-only"
        
        placeholder_content = f'''<!-- File: {template_path} -->
<!-- Revision: 1.0 - {template_type} template for {template_name} -->

{{% extends "base.html" %}} 
{{% block title %}}{template_name.title()} - Outfit Manager{{% endblock %}}

{{% block content %}}
<div class="container">
    <div class="page-header">
        <h2 class="page-title">{template_name.replace('_', ' ').title()}</h2>
    </div>
    
    <div class="empty-state">
        <div class="empty-content">
            <span class="empty-icon">🚧</span>
            <h3>Template Placeholder</h3>
            <p>This template ({template_path}) needs to be implemented with proper content.</p>
        </div>
    </div>
</div>
{{% endblock %}}
'''
        
        # For content-only templates, don't extend base
        if "_content" in template_path:
            placeholder_content = f'''<!-- File: {template_path} -->
<!-- Revision: 1.0 - {template_type} template for {template_name} -->

<div class="container">
    <div class="page-header">
        <h2 class="page-title">{template_name.replace('_', ' ').title()}</h2>
    </div>
    
    <div class="empty-state">
        <div class="empty-content">
            <span class="empty-icon">🚧</span>
            <h3>Template Placeholder</h3>
            <p>This template ({template_path}) needs to be implemented with proper content.</p>
        </div>
    </div>
</div>
'''
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(placeholder_content)
        print(f"✅ Created: {template_path} (placeholder)")

def main():
    """Create the complete outfit manager project structure"""
    
    print("🎯 OUTFIT MANAGER - PROJECT SETUP")
    print("=" * 50)
    print("Creating complete project structure with starter content...")
    print()
    
    try:
        create_directory_structure()
        create_python_files()
        create_router_files()
        create_service_files()
        create_static_files()
        create_template_files()
        
        print("\n" + "=" * 50)
        print("🎉 PROJECT SETUP COMPLETE!")
        print("=" * 50)
        
        print("\n📋 Next Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python main.py")
        print("3. Open browser to: http://localhost:8000")
        print("4. Replace placeholder templates with full implementations")
        print("5. Run debug.py to validate structure")
        
        print("\n📝 Notes:")
        print("- All Python files have proper headers and basic functionality")
        print("- Templates include both full-page and HTMX content-only versions")
        print("- Complex templates are created as placeholders - implement with full content")
        print("- CSS includes complete purple design system")
        print("- HTMX integration is ready to use")
        print("- Image upload service is implemented")
        
        print("\n🚀 Ready to build your outfit management system!")
        
    except Exception as e:
        print(f"\n💥 Error during setup: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()