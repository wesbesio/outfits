# File: main.py
# Revision: 1.3 - Added Outfit Router

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from models.database import create_db_and_tables, engine, get_session
from services.seed_data import seed_initial_data
# Import new routers
from routers import components, images, outfits # Added outfits

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
    response = RedirectResponse(url="/components/", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["HX-Redirect"] = "/components/"
    return response

# Include routers
app.include_router(components.router)
app.include_router(images.router)
app.include_router(outfits.router) # Added this line
# Placeholder for other router includes (vendors, pieces)
# from routers import vendors, pieces
# app.include_router(vendors.router)
# app.include_router(pieces.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)