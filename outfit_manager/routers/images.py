# File: routers/images.py
# Revision: 1.0 - Endpoint to serve BLOB images

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlmodel import Session, select
from typing import Union

from models import Component, Outfit
from models.database import get_session

router = APIRouter()

@router.get("/api/images/{model_name}/{item_id}")
async def get_image(
    model_name: str,
    item_id: int,
    session: Session = Depends(get_session)
) -> Response:
    """
    Serves an image BLOB from the database based on model name and item ID.
    Supports 'components' and 'outfits'.
    """
    image_data: Optional[bytes] = None

    if model_name.lower() == "components":
        item = session.get(Component, item_id)
        if item:
            image_data = item.image
    elif model_name.lower() == "outfits":
        item = session.get(Outfit, item_id)
        if item:
            image_data = item.image
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model name. Must be 'components' or 'outfits'."
        )

    if not image_data:
        # Return a placeholder or 404 if no image found
        # You could also serve a default placeholder image here
        # For simplicity, returning 204 No Content or a 404.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image for {model_name} with ID {item_id} not found."
        )

    # Assuming images are stored as JPEG (due to processing in ImageService)
    return Response(content=image_data, media_type="image/jpeg")