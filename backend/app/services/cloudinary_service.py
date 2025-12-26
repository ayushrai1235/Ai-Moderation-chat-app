import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

class CloudinaryService:
    settings = settings

    @staticmethod
    def upload_file(file, folder="chat_app"):
        """Upload a file to Cloudinary."""
        try:
            response = cloudinary.uploader.upload(file, folder=folder, resource_type="auto")
            return {
                "url": response.get("secure_url"),
                "public_id": response.get("public_id"),
                "format": response.get("format"),
                "resource_type": response.get("resource_type")
            }
        except Exception as e:
            print(f"Cloudinary Upload Error: {e}")
            return None

    @staticmethod
    def generate_signature(params_to_sign):
        """Generate a signature for client-side uploads."""
        return cloudinary.utils.api_sign_request(params_to_sign, settings.CLOUDINARY_API_SECRET)

cloudinary_service = CloudinaryService()
