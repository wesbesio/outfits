# File: services/image_service.py
# Revision: 1.1 - Added missing imports for typing module

from PIL import Image
from io import BytesIO
from typing import Optional, List, Dict, Any # Added Optional, List, Dict, Any

class ImageService:
    MAX_FILE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_FORMATS = {"jpeg", "png", "webp", "gif"}
    MAX_IMAGE_DIMENSION = 1000 # Max width/height for processed images
    THUMBNAIL_DIMENSION = 200 # For potential future thumbnail use or display

    @staticmethod
    def validate_and_process_image(image_bytes: bytes, filename: str) -> Optional[bytes]:
        """
        Validates an image, processes it (resizes, converts to JPEG), and returns
        the processed image bytes. Returns None if validation fails or processing errors.
        """
        if not image_bytes:
            return None

        # 1. Validate file size
        if len(image_bytes) > ImageService.MAX_FILE_SIZE_BYTES:
            print(f"Image size exceeds limit: {len(image_bytes) / (1024*1024):.2f}MB > {ImageService.MAX_FILE_SIZE_MB}MB")
            return None

        try:
            img = Image.open(BytesIO(image_bytes))
            img.verify() # Verify file integrity
            img = Image.open(BytesIO(image_bytes)) # Re-open after verify to avoid error after verify() closes the file

            # 2. Validate format
            if img.format.lower() not in ImageService.ALLOWED_FORMATS:
                print(f"Unsupported image format: {img.format}. Allowed: {ImageService.ALLOWED_FORMATS}")
                return None

            # 3. Process image (resize and convert to JPEG)
            img = img.convert("RGB") # Ensure it's RGB for JPEG conversion

            # Calculate new dimensions while maintaining aspect ratio
            width, height = img.size
            if width > ImageService.MAX_IMAGE_DIMENSION or height > ImageService.MAX_IMAGE_DIMENSION:
                if width > height:
                    new_width = ImageService.MAX_IMAGE_DIMENSION
                    new_height = int(new_width * (height / width))
                else:
                    new_height = ImageService.MAX_IMAGE_DIMENSION
                    new_width = int(new_height * (width / height))
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save as JPEG with optimized compression
            output_buffer = BytesIO()
            img.save(output_buffer, format="JPEG", quality=85, optimize=True) # quality 85 is usually a good balance
            output_buffer.seek(0)
            return output_buffer.getvalue()

        except Exception as e:
            print(f"Error processing image {filename}: {e}")
            return None

    @staticmethod
    def get_image_info(image_bytes: bytes) -> Dict[str, Any]:
        """
        Returns basic image information (width, height, format, size)
        without full processing.
        """
        if not image_bytes:
            return {}
        try:
            img = Image.open(BytesIO(image_bytes))
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "size_bytes": len(image_bytes)
            }
        except Exception:
            return {}