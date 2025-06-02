# File: services/image_service.py
# Revision: 1.0 - Image processing utilities

from PIL import Image
from io import BytesIO
from fastapi import UploadFile, HTTPException
from typing import Optional

class ImageService:
    """Service for handling image uploads and processing."""
    
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
    MAX_IMAGE_SIZE = (1200, 1200)
    THUMBNAIL_SIZE = (300, 300)
    
    @classmethod
    async def validate_and_process_image(cls, file: UploadFile) -> bytes:
        """Validate and process uploaded image."""
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
        """Create thumbnail from image data."""
        try:
            image = Image.open(BytesIO(image_data))
            image.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            output = BytesIO()
            image.save(output, format='JPEG', quality=80)
            output.seek(0)
            
            return output.read()
        except Exception:
            return image_data  # Return original if thumbnail creation fails
