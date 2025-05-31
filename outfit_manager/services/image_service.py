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

    @classmethod
    def bytes_to_image_response(cls, image_data: Optional[bytes]) -> Optional[bytes]:
        """Convert BLOB data to image response format"""
        if not image_data:
            return None
        return image_data

    @classmethod
    def validate_file_type(cls, filename: str) -> bool:
        """Validate file extension"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        extension = filename.lower().split('.')[-1] if '.' in filename else ''
        return f'.{extension}' in allowed_extensions