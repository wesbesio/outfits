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

@router.get("/placeholder/{item_type}")
async def get_placeholder_image(item_type: str):
    """Serve placeholder images for items without photos"""
    # This would serve default placeholder images
    # For now, return a simple response
    if item_type not in ["component", "outfit"]:
        raise HTTPException(status_code=400, detail="Invalid item type")
    
    # In a real implementation, you'd serve actual placeholder image files
    raise HTTPException(status_code=404, detail="Placeholder image not implemented")

@router.head("/component/{component_id}")
async def check_component_image(
    component_id: int,
    session: Session = Depends(get_session)
):
    """Check if component has an image (HEAD request)"""
    component = session.get(Component, component_id)
    
    if not component or not component.image:
        raise HTTPException(status_code=404, detail="No image found")
    
    return Response(
        headers={
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(component.image))
        }
    )

@router.head("/outfit/{outfit_id}")
async def check_outfit_image(
    outfit_id: int,
    session: Session = Depends(get_session)
):
    """Check if outfit has an image (HEAD request)"""
    outfit = session.get(Outfit, outfit_id)
    
    if not outfit or not outfit.image:
        raise HTTPException(status_code=404, detail="No image found")
    
    return Response(
        headers={
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(outfit.image))
        }
    )