from fastapi.responses import HTMLResponse
from fastapi import Request

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import uvicorn

from models.database import create_db_and_tables, get_session
from routers import outfits, components, vendors, images, pieces
from services.seed_data import create_seed_data

# Debug: Try to import web_routes separately
try:
    from routers import web_routes
    print("✅ web_routes imported successfully")
    print(f"✅ web_routes.router type: {type(web_routes.router)}")
except Exception as e:
    print(f"❌ Error importing web_routes: {e}")
    import traceback
    traceback.print_exc()
    web_routes = None

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

# Include web page routes FIRST (if successfully imported)
if web_routes:
    try:
        app.include_router(web_routes.router, tags=["web"])
        print("✅ web_routes.router registered successfully")
    except Exception as e:
        print(f"❌ Error registering web_routes: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Skipping web_routes registration - import failed")

# Include API routers AFTER web routes
app.include_router(outfits.router, prefix="/api/outfits", tags=["outfits"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(pieces.router, prefix="/api/pieces", tags=["pieces"])
app.include_router(images.router, prefix="/api/images", tags=["images"])

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Simple test route to verify FastAPI is working
@app.get("/test/main-routes-working")
async def test_main_routes():
    return {"message": "Main routes working!", "web_routes_loaded": web_routes is not None}

# Debug endpoint to see all registered routes
@app.get("/debug/all-registered-routes")
async def debug_all_routes():
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'Unknown')
            })
    
    # Filter for relevant routes
    redirect_routes = [r for r in routes_info if '/new' in r['path']]
    form_routes = [r for r in routes_info if '/forms/' in r['path']]
    test_routes = [r for r in routes_info if '/test/' in r['path']]
    
    return {
        "total_routes": len(routes_info),
        "redirect_routes": redirect_routes,
        "form_routes": form_routes,
        "test_routes": test_routes
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)