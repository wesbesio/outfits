# File: setup.py
# Revision: 1.0 - Project structure initialization script

import os
from pathlib import Path

def create_directories():
    """Create all required directories for the Outfit Manager project."""
    directories = [
        "outfit_manager",
        "outfit_manager/models",
        "outfit_manager/routers", 
        "outfit_manager/services",
        "outfit_manager/templates",
        "outfit_manager/templates/components",
        "outfit_manager/templates/outfits",
        "outfit_manager/templates/forms",
        "outfit_manager/templates/partials",
        "outfit_manager/static",
        "outfit_manager/static/css",
        "outfit_manager/static/js"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_python_files():
    """Create Python files with basic structure."""
    
    # Main FastAPI application
    main_py = """# File: main.py
# Revision: 1.0 - FastAPI application setup

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

from models.database import init_db
from routers import components, outfits, vendors, pieces, images

# Initialize FastAPI app
app = FastAPI(
    title="Outfit Manager",
    description="Modern fashion outfit management system",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(outfits.router, prefix="/api/outfits", tags=["outfits"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(pieces.router, prefix="/api/pieces", tags=["pieces"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

@app.on_event("startup")
async def startup_event():
    \"\"\"Initialize database on startup.\"\"\"
    init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    \"\"\"Home page route.\"\"\"
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/components", response_class=HTMLResponse)
async def components_page(request: Request):
    \"\"\"Components list page.\"\"\"
    return templates.TemplateResponse("components/list.html", {"request": request})

@app.get("/outfits", response_class=HTMLResponse)
async def outfits_page(request: Request):
    \"\"\"Outfits list page.\"\"\"
    return templates.TemplateResponse("outfits/list.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"""

    # Requirements.txt
    requirements = """# File: requirements.txt
# Revision: 1.0 - Python dependencies

fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
pillow==10.1.0
jinja2==3.1.2
python-multipart==0.0.6
aiofiles==23.2.1
"""

    # Models __init__.py
    models_init = """# File: models/__init__.py
# Revision: 1.0 - SQLModel definitions

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Vendor(SQLModel, table=True):
    \"\"\"Vendor model for shopping sources.\"\"\"
    venid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="vendor")
    outfits: List["Outfit"] = Relationship(back_populates="vendor")

class Piece(SQLModel, table=True):
    \"\"\"Piece model for clothing categories.\"\"\"
    piecid: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    active: bool = Field(default=True)
    
    # Relationships
    components: List["Component"] = Relationship(back_populates="piece")

class Component(SQLModel, table=True):
    \"\"\"Component model for individual clothing items.\"\"\"
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
    \"\"\"Outfit model for collections of components.\"\"\"
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
    \"\"\"Many-to-many relationship between outfits and components.\"\"\"
    o2cid: Optional[int] = Field(default=None, primary_key=True)
    outid: int = Field(foreign_key="outfit.outid")
    comid: int = Field(foreign_key="component.comid")
    active: bool = Field(default=True)
    flag: bool = Field(default=False)
    
    # Relationships
    outfit: Outfit = Relationship(back_populates="component_links")
    component: Component = Relationship(back_populates="outfit_links")
"""

    # Database configuration
    database_py = """# File: models/database.py
# Revision: 1.0 - Database configuration

from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

# Database file path
DB_PATH = Path("outfit_manager.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production
)

def init_db():
    \"\"\"Initialize database and create all tables.\"\"\"
    SQLModel.metadata.create_all(engine)

def get_session():
    \"\"\"Get database session.\"\"\"
    with Session(engine) as session:
        yield session
"""

    # Debug script
    debug_py = """# File: debug.py
# Revision: 1.0 - Project validation script

import os
from pathlib import Path
import importlib.util

def check_file_structure():
    \"\"\"Check if all required files and directories exist.\"\"\"
    required_structure = [
        "main.py",
        "requirements.txt",
        "models/__init__.py",
        "models/database.py",
        "routers/__init__.py",
        "routers/components.py",
        "routers/outfits.py", 
        "routers/vendors.py",
        "routers/pieces.py",
        "routers/images.py",
        "services/__init__.py",
        "services/image_service.py",
        "services/seed_data.py",
        "templates/base.html",
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
        "templates/forms/vendor_form_content.html",
        "templates/partials/component_cards.html",
        "templates/partials/outfit_cards.html",
        "templates/partials/vendor_options.html",
        "templates/partials/piece_options.html",
        "static/css/main.css",
        "static/js/main.js",
        "static/js/form-error-handler.js"
    ]
    
    missing_files = []
    for file_path in required_structure:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_python_imports():
    \"\"\"Check if Python modules can be imported.\"\"\"
    modules_to_check = [
        "models",
        "models.database",
        "routers.components",
        "routers.outfits",
        "services.image_service"
    ]
    
    failed_imports = []
    for module_name in modules_to_check:
        try:
            if Path(f"{module_name.replace('.', '/')}.py").exists():
                spec = importlib.util.spec_from_file_location(
                    module_name, 
                    f"{module_name.replace('.', '/')}.py"
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {module_name} imports successfully")
        except Exception as e:
            failed_imports.append((module_name, str(e)))
            print(f"❌ {module_name} failed to import: {e}")
    
    return len(failed_imports) == 0

def check_template_structure():
    \"\"\"Check if templates have proper structure.\"\"\"
    print("\\n📋 Template Structure Check:")
    
    base_template = Path("templates/base.html")
    if base_template.exists():
        content = base_template.read_text()
        if "htmx.org" in content:
            print("✅ Base template includes HTMX")
        else:
            print("❌ Base template missing HTMX")
            
        if "main-content" in content:
            print("✅ Base template has main-content div")
        else:
            print("❌ Base template missing main-content div")
    else:
        print("❌ Base template not found")

def main():
    \"\"\"Run all validation checks.\"\"\"
    print("🔍 Outfit Manager Project Validation\\n")
    
    print("📁 File Structure Check:")
    structure_ok = check_file_structure()
    
    print("\\n🐍 Python Import Check:")
    imports_ok = check_python_imports()
    
    check_template_structure()
    
    print("\\n" + "="*50)
    if structure_ok and imports_ok:
        print("🎉 Project validation successful!")
        print("✅ Ready for Phase 1 implementation")
    else:
        print("⚠️  Project validation failed")
        print("❌ Fix issues before proceeding")

if __name__ == "__main__":
    main()
"""

    files_to_create = [
        ("outfit_manager/main.py", main_py),
        ("outfit_manager/requirements.txt", requirements),
        ("outfit_manager/models/__init__.py", models_init),
        ("outfit_manager/models/database.py", database_py),
        ("outfit_manager/debug.py", debug_py)
    ]
    
    for file_path, content in files_to_create:
        Path(file_path).write_text(content)
        print(f"✓ Created: {file_path}")

def create_router_files():
    """Create router files with basic structure."""
    
    # Router __init__.py
    router_init = """# File: routers/__init__.py
# Revision: 1.0 - Router module initialization
"""

    # Components router
    components_router = """# File: routers/components.py
# Revision: 1.0 - Component CRUD operations

from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional, List

from models import Component, Vendor, Piece
from models.database import get_session

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def list_components(request: Request, session: Session = Depends(get_session)):
    \"\"\"List all components with filtering options.\"\"\"
    components = session.exec(select(Component).where(Component.active == True)).all()
    return templates.TemplateResponse(
        "components/list_content.html", 
        {"request": request, "components": components}
    )

@router.post("/", response_class=HTMLResponse)
async def create_component(
    request: Request,
    name: str = Form(...),
    brand: Optional[str] = Form(None),
    cost: int = Form(0),
    description: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    vendorid: Optional[int] = Form(None),
    piecid: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session)
):
    \"\"\"Create a new component.\"\"\"
    # TODO: Implement image processing
    image_data = None
    if file and file.content_type.startswith('image/'):
        image_data = await file.read()
    
    component = Component(
        name=name,
        brand=brand,
        cost=cost,
        description=description,
        notes=notes,
        vendorid=vendorid,
        piecid=piecid,
        image=image_data
    )
    
    session.add(component)
    session.commit()
    session.refresh(component)
    
    # Redirect to components list
    return templates.TemplateResponse(
        "components/list.html",
        {"request": request, "message": "Component created successfully"}
    )

@router.get("/{component_id}", response_class=HTMLResponse)
async def get_component(
    request: Request, 
    component_id: int, 
    session: Session = Depends(get_session)
):
    \"\"\"Get component details.\"\"\"
    component = session.get(Component, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return templates.TemplateResponse(
        "components/detail_content.html",
        {"request": request, "component": component}
    )
"""

    # Similar structure for other routers
    routers = [
        ("outfit_manager/routers/__init__.py", router_init),
        ("outfit_manager/routers/components.py", components_router),
        ("outfit_manager/routers/outfits.py", router_init.replace("Router module initialization", "Outfit CRUD operations")),
        ("outfit_manager/routers/vendors.py", router_init.replace("Router module initialization", "Vendor management")),
        ("outfit_manager/routers/pieces.py", router_init.replace("Router module initialization", "Piece type management")),
        ("outfit_manager/routers/images.py", router_init.replace("Router module initialization", "Image serving endpoints"))
    ]
    
    for file_path, content in routers:
        Path(file_path).write_text(content)
        print(f"✓ Created: {file_path}")

def create_service_files():
    """Create service files with basic structure."""
    
    services_init = """# File: services/__init__.py
# Revision: 1.0 - Services module initialization
"""

    image_service = """# File: services/image_service.py
# Revision: 1.0 - Image processing utilities

from PIL import Image
from io import BytesIO
from fastapi import UploadFile, HTTPException
from typing import Optional

class ImageService:
    \"\"\"Service for handling image uploads and processing.\"\"\"
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_IMAGE_SIZE = (1200, 1200)
    THUMBNAIL_SIZE = (300, 300)
    
    @classmethod
    async def validate_and_process_image(cls, file: UploadFile) -> bytes:
        \"\"\"Validate and process uploaded image.\"\"\"
        # Check file size
        if file.size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Read file content
        content = await file.read()
        
        try:
            # Open and validate image
            image = Image.open(BytesIO(content))
            
            # Check format
            if image.format not in cls.ALLOWED_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported image format. Allowed: {', '.join(cls.ALLOWED_FORMATS)}"
                )
            
            # Resize if necessary
            if image.size[0] > cls.MAX_IMAGE_SIZE[0] or image.size[1] > cls.MAX_IMAGE_SIZE[1]:
                image.thumbnail(cls.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary and save as JPEG
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save processed image
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.read()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    @classmethod
    def create_thumbnail(cls, image_data: bytes) -> bytes:
        \"\"\"Create thumbnail from image data.\"\"\"
        try:
            image = Image.open(BytesIO(image_data))
            image.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            image.save(output, format='JPEG', quality=80)
            output.seek(0)
            
            return output.read()
        except Exception:
            return image_data  # Return original if thumbnail creation fails
"""

    seed_data = """# File: services/seed_data.py
# Revision: 1.0 - Initial data creation

from sqlmodel import Session
from models import Vendor, Piece
from models.database import engine

def create_initial_vendors():
    \"\"\"Create initial vendor data.\"\"\"
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
    \"\"\"Create initial piece type data.\"\"\"
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
    \"\"\"Seed database with initial data.\"\"\"
    print("🌱 Seeding database with initial data...")
    
    create_initial_vendors()
    print("✅ Created initial vendors")
    
    create_initial_pieces()
    print("✅ Created initial piece types")
    
    print("🎉 Database seeding complete!")

if __name__ == "__main__":
    seed_database()
"""

    services = [
        ("outfit_manager/services/__init__.py", services_init),
        ("outfit_manager/services/image_service.py", image_service),
        ("outfit_manager/services/seed_data.py", seed_data)
    ]
    
    for file_path, content in services:
        Path(file_path).write_text(content)
        print(f"✓ Created: {file_path}")

def create_template_files():
    """Create HTML template files."""
    
    base_template = """<!-- File: templates/base.html -->
<!-- Revision: 1.0 - Base template with HTMX integration -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Outfit Manager{% endblock %}</title>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.6"></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/static/css/main.css">
    
    <!-- Meta tags for mobile -->
    <meta name="description" content="Modern fashion outfit management system">
    <meta name="theme-color" content="#8B5CF6">
</head>
<body class="bg-gradient">
    <!-- Header Navigation -->
    <header class="header">
        <nav class="nav-container">
            <div class="nav-brand">
                <h1>👗 Outfit Manager</h1>
            </div>
            
            <div class="nav-links">
                <a href="/" hx-get="/" hx-target="#main-content" hx-swap="innerHTML" class="nav-link">Home</a>
                <a href="/components" hx-get="/api/components/" hx-target="#main-content" hx-swap="innerHTML" class="nav-link">Components</a>
                <a href="/outfits" hx-get="/api/outfits/" hx-target="#main-content" hx-swap="innerHTML" class="nav-link">Outfits</a>
            </div>
        </nav>
    </header>

    <!-- Main Content Area -->
    <main id="main-content" class="main-content">
        {% block content %}
        <div class="welcome-container">
            <h2>Welcome to Outfit Manager</h2>
            <p>Organize your wardrobe with style!</p>
            
            <div class="action-cards">
                <div class="action-card" hx-get="/api/components/" hx-target="#main-content" hx-swap="innerHTML">
                    <h3>📦 Components</h3>
                    <p>Manage your clothing items</p>
                </div>
                
                <div class="action-card" hx-get="/api/outfits/" hx-target="#main-content" hx-swap="innerHTML">
                    <h3>👕 Outfits</h3>
                    <p>Create and organize outfits</p>
                </div>
            </div>
        </div>
        {% endblock %}
    </main>

    <!-- Bottom Navigation (Mobile) -->
    <nav class="bottom-nav">
        <a href="/" hx-get="/" hx-target="#main-content" hx-swap="innerHTML" class="bottom-nav-item">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">Home</span>
        </a>
        <a href="/components" hx-get="/api/components/" hx-target="#main-content" hx-swap="innerHTML" class="bottom-nav-item">
            <span class="nav-icon">📦</span>
            <span class="nav-label">Components</span>
        </a>
        <a href="/outfits" hx-get="/api/outfits/" hx-target="#main-content" hx-swap="innerHTML" class="bottom-nav-item">
            <span class="nav-icon">👕</span>
            <span class="nav-label">Outfits</span>
        </a>
    </nav>

    <!-- Custom JavaScript -->
    <script src="/static/js/main.js"></script>
</body>
</html>
"""

    # Create basic template structure for all template files
    templates = [
        ("outfit_manager/templates/base.html", base_template),
        # Components templates
        ("outfit_manager/templates/components/list.html", "<!-- Component list full page -->"),
        ("outfit_manager/templates/components/list_content.html", "<!-- Component list content only -->"),
        ("outfit_manager/templates/components/detail.html", "<!-- Component detail full page -->"),
        ("outfit_manager/templates/components/detail_content.html", "<!-- Component detail content only -->"),
        # Outfits templates  
        ("outfit_manager/templates/outfits/list.html", "<!-- Outfit list full page -->"),
        ("outfit_manager/templates/outfits/list_content.html", "<!-- Outfit list content only -->"),
        ("outfit_manager/templates/outfits/detail.html", "<!-- Outfit detail full page -->"),
        ("outfit_manager/templates/outfits/detail_content.html", "<!-- Outfit detail content only -->"),
        # Form templates
        ("outfit_manager/templates/forms/component_form.html", "<!-- Component form full page -->"),
        ("outfit_manager/templates/forms/component_form_content.html", "<!-- Component form content only -->"),
        ("outfit_manager/templates/forms/outfit_form.html", "<!-- Outfit form full page -->"),
        ("outfit_manager/templates/forms/outfit_form_content.html", "<!-- Outfit form content only -->"),
        ("outfit_manager/templates/forms/vendor_form.html", "<!-- Vendor form full page -->"),
        ("outfit_manager/templates/forms/vendor_form_content.html", "<!-- Vendor form content only -->"),
        # Partial templates
        ("outfit_manager/templates/partials/component_cards.html", "<!-- Component cards partial -->"),
        ("outfit_manager/templates/partials/outfit_cards.html", "<!-- Outfit cards partial -->"),
        ("outfit_manager/templates/partials/vendor_options.html", "<!-- Vendor options partial -->"),
        ("outfit_manager/templates/partials/piece_options.html", "<!-- Piece options partial -->")
    ]
    
    for file_path, content in templates:
        Path(file_path).write_text(content)
        print(f"✓ Created: {file_path}")

def create_static_files():
    """Create CSS and JavaScript files."""
    
    main_css = """/* File: static/css/main.css */
/* Revision: 1.0 - Complete design system */

/* CSS Custom Properties */
:root {
    /* Color Palette */
    --primary-color: #8B5CF6;      /* Main purple */
    --primary-dark: #7C3AED;       /* Darker purple */
    --primary-light: #A78BFA;      /* Lighter purple */
    --secondary-color: #EC4899;    /* Pink accent */
    --accent-color: #F3E8FF;       /* Light purple */
    
    /* Gradients */
    --bg-gradient: linear-gradient(135deg, #F3E8FF 0%, #E0E7FF 50%, #F0F4FF 100%);
    --card-gradient: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.8) 100%);
    
    /* Background Colors */
    --card-bg: rgba(255, 255, 255, 0.9);
    --overlay-bg: rgba(0, 0, 0, 0.1);
    
    /* Text Colors */
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --text-light: #9CA3AF;
    
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
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    
    /* Transitions */
    --transition-fast: 150ms ease-in-out;
    --transition-normal: 250ms ease-in-out;
    --transition-slow: 350ms ease-in-out;
}

/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
}

.bg-gradient {
    background: var(--bg-gradient);
    min-height: 100vh;
}

/* Header Styles */
.header {
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
    background: rgba(255, 255, 255, 0.8);
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-md) var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h1 {
    color: var(--primary-color);
    font-size: 1.5rem;
    font-weight: 700;
}

.nav-links {
    display: flex;
    gap: var(--spacing-lg);
}

.nav-link {
    color: var(--text-primary);
    text-decoration: none;
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    min-height: 44px;
    display: flex;
    align-items: center;
}

.nav-link:hover {
    background: var(--accent-color);
    color: var(--primary-dark);
    transform: translateY(-1px);
}

/* Main Content */
.main-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-xl) var(--spacing-lg);
    min-height: calc(100vh - 140px);
}

/* Welcome Container */
.welcome-container {
    text-align: center;
    padding: var(--spacing-2xl);
}

.welcome-container h2 {
    color: var(--primary-color);
    font-size: 2.5rem;
    margin-bottom: var(--spacing-md);
    font-weight: 700;
}

.welcome-container p {
    color: var(--text-secondary);
    font-size: 1.125rem;
    margin-bottom: var(--spacing-2xl);
}

/* Action Cards */
.action-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-xl);
    margin-top: var(--spacing-2xl);
}

.action-card {
    background: var(--card-gradient);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-lg);
    border: 1px solid rgba(139, 92, 246, 0.1);
    cursor: pointer;
    transition: all var(--transition-normal);
    text-align: center;
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.action-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    border-color: var(--primary-light);
}

.action-card h3 {
    color: var(--primary-color);
    font-size: 1.25rem;
    margin-bottom: var(--spacing-sm);
    font-weight: 600;
}

.action-card p {
    color: var(--text-secondary);
}

/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(139, 92, 246, 0.1);
    display: flex;
    justify-content: space-around;
    padding: var(--spacing-sm) 0;
    z-index: 100;
}

.bottom-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-decoration: none;
    color: var(--text-secondary);
    transition: all var(--transition-fast);
    padding: var(--spacing-sm);
    min-width: 44px;
    min-height: 44px;
}

.bottom-nav-item:hover {
    color: var(--primary-color);
    transform: translateY(-2px);
}

.nav-icon {
    font-size: 1.25rem;
    margin-bottom: var(--spacing-xs);
}

.nav-label {
    font-size: 0.75rem;
    font-weight: 500;
}

/* Responsive Design */
@media (min-width: 768px) {
    .bottom-nav {
        display: none;
    }
    
    .main-content {
        padding-bottom: var(--spacing-xl);
    }
}

@media (max-width: 767px) {
    .nav-links {
        display: none;
    }
    
    .main-content {
        padding-bottom: 80px;
    }
    
    .welcome-container h2 {
        font-size: 2rem;
    }
    
    .action-cards {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }
}

/* Utility Classes */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}

/* HTMX Loading Indicators */
.htmx-indicator {
    opacity: 0;
    transition: opacity var(--transition-fast);
}

.htmx-request .htmx-indicator {
    opacity: 1;
}

.htmx-request.htmx-indicator {
    opacity: 1;
}
"""

    main_js = """// File: static/js/main.js
// Revision: 1.0 - Minimal utilities only

// HTMX Configuration
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX defaults
    htmx.config.globalViewTransitions = true;
    htmx.config.defaultSwapStyle = 'innerHTML';
    
    // Add loading states
    document.addEventListener('htmx:beforeRequest', function(evt) {
        const target = evt.target;
        target.classList.add('htmx-loading');
    });
    
    document.addEventListener('htmx:afterRequest', function(evt) {
        const target = evt.target;
        target.classList.remove('htmx-loading');
    });
    
    // Handle navigation active states
    document.addEventListener('htmx:afterSettle', function(evt) {
        updateActiveNavigation();
    });
});

// Update active navigation states
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .bottom-nav-item');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath.includes(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
}

// Initialize on page load
updateActiveNavigation();
"""

    form_error_handler = """// File: static/js/form-error-handler.js
// Revision: 1.0 - HTMX error handling

// Handle HTMX errors
document.addEventListener('htmx:responseError', function(evt) {
    console.error('HTMX Response Error:', evt.detail);
    
    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = 'Something went wrong. Please try again.';
    
    const target = evt.target;
    target.insertBefore(errorDiv, target.firstChild);
    
    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
});

// Handle validation errors
document.addEventListener('htmx:afterRequest', function(evt) {
    if (evt.detail.xhr.status === 422) {
        // Handle validation errors
        try {
            const errors = JSON.parse(evt.detail.xhr.responseText);
            displayValidationErrors(errors);
        } catch (e) {
            console.error('Error parsing validation response:', e);
        }
    }
});

function displayValidationErrors(errors) {
    // Clear existing errors
    document.querySelectorAll('.field-error').forEach(el => el.remove());
    
    // Display new errors
    if (errors.detail) {
        errors.detail.forEach(error => {
            const field = document.querySelector(`[name="${error.loc[1]}"]`);
            if (field) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = error.msg;
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
        });
    }
}
"""

    static_files = [
        ("outfit_manager/static/css/main.css", main_css),
        ("outfit_manager/static/js/main.js", main_js),
        ("outfit_manager/static/js/form-error-handler.js", form_error_handler)
    ]
    
    for file_path, content in static_files:
        Path(file_path).write_text(content)
        print(f"✓ Created: {file_path}")

def main():
    """Main setup function."""
    print("🚀 Setting up Outfit Manager project structure...")
    print()
    
    # Create all directories
    create_directories()
    print()
    
    # Create Python files
    print("📝 Creating Python files...")
    create_python_files()
    print()
    
    # Create router files
    print("🔄 Creating router files...")
    create_router_files()
    print()
    
    # Create service files
    print("⚙️ Creating service files...")
    create_service_files()
    print()
    
    # Create template files
    print("🎨 Creating template files...")
    create_template_files()
    print()
    
    # Create static files
    print("💄 Creating static files...")
    create_static_files()
    print()
    
    print("🎉 Project setup complete!")
    print()
    print("Next steps:")
    print("1. cd outfit_manager")
    print("2. pip install -r requirements.txt")
    print("3. python debug.py")
    print("4. python services/seed_data.py")
    print("5. python main.py")

if __name__ == "__main__":
    main()