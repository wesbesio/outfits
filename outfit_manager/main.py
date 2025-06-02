# File: main.py
# Revision: 1.2 - Added RedirectResponse and status imports, updated root to redirect to components

from fastapi import FastAPI, Request, Depends, status # Added status
from fastapi.responses import HTMLResponse, RedirectResponse # Added RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from models.database import create_db_and_tables, engine, get_session
from services.seed_data import seed_initial_data
# Import new routers
from routers import components, images

# Initialize FastAPI app
app = FastAPI(
    title="Outfit Manager",
    description="A modern fashion outfit management system using FastAPI + HTMX.",
    version="1.0.0"
)

# Mount static files (ensure `static/images/placeholder.svg` exists if you use it)
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
    This will serve as the initial entry point for the HTMX application.
    """
    # HTMX will then load content into the main-content block.
    # We can directly redirect to the components list from the root
    response = RedirectResponse(url="/components/", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = "/components/"
    return response

# Include routers
app.include_router(components.router)
app.include_router(images.router)
# Placeholder for other router includes (outfits, vendors, pieces)
# from routers import outfits, vendors, pieces
# app.include_router(outfits.router)
# app.include_router(vendors.router)
# app.include_router(pieces.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)