# File: main.py
# Revision: 2.0 - Added Vendor Router

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from models.database import create_db_and_tables, engine, get_session
from services.seed_data import seed_initial_data
# Import routers
from routers import components, images, outfits, vendors

# Initialize FastAPI app
app = FastAPI(
    title="Outfit Manager",
    description="A modern fashion outfit management system using FastAPI + HTMX.",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    """Event handler for application startup."""
    print("Application startup: Creating database and tables...")
    create_db_and_tables()
    with Session(engine) as session:
        seed_initial_data(session)
    print("Application startup complete.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, session: Session = Depends(get_session)):
    """
    Root endpoint serving the base HTML page.
    Redirects to the components list by default.
    """
    response = RedirectResponse(url="/components/", status_code=status.HTTP_303_SEE_OTHER)
    return response

# Include routers
app.include_router(components.router, tags=["Components"])
app.include_router(images.router, tags=["Images"])
app.include_router(outfits.router, tags=["Outfits"])
app.include_router(vendors.router, tags=["Vendors"])

# Placeholder for other router includes (pieces)
# from routers import pieces 
# app.include_router(pieces.router, prefix="/pieces", tags=["Pieces"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)