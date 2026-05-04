import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


async def upload_image(file: UploadFile, folder: str = "presence/students") -> str:
    """Upload an image to Cloudinary and return the URL."""
    try:
        # Read file content
        content = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder=folder,
            resource_type="image",
            transformation=[
                {"width": 500, "height": 500, "crop": "fill", "gravity": "face"},
                {"quality": "auto:good"}
            ]
        )
        
        return result["secure_url"]
    except Exception as e:
        logger.error(f"Cloudinary upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


async def upload_group_image(file: UploadFile) -> str:
    """Upload a group photo for attendance processing."""
    try:
        content = await file.read()
        
        result = cloudinary.uploader.upload(
            content,
            folder="presence/attendance",
            resource_type="image",
            transformation=[
                {"quality": "auto:best"}  # Keep high quality for face recognition
            ]
        )
        
        return result["secure_url"]
    except Exception as e:
        logger.error(f"Cloudinary upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


def delete_image(public_id: str) -> bool:
    """Delete an image from Cloudinary."""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Cloudinary delete error: {str(e)}")
        return False
