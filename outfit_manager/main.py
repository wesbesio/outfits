# File: main.py
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
    """Initialize database on startup."""
    init_db()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page route."""
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/components", response_class=HTMLResponse)
async def components_page(request: Request):
    """Components list page."""
    return templates.TemplateResponse("components/list.html", {"request": request})

@app.get("/outfits", response_class=HTMLResponse)
async def outfits_page(request: Request):
    """Outfits list page."""
    return templates.TemplateResponse("outfits/list.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
