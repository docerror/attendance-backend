# from pydantic_settings import BaseSettings
# from functools import lru_cache
# import os


# class Settings(BaseSettings):
#     # Database
#     database_url: str = "postgresql://user:password@localhost:5432/presence"
    
#     # JWT
#     secret_key: str = "your-super-secret-key-change-in-production"
#     algorithm: str = "HS256"
#     access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
#     # Cloudinary
#     cloudinary_cloud_name: str = ""
#     cloudinary_api_key: str = ""
#     cloudinary_api_secret: str = ""
    
#     # Email (SMTP)
#     smtp_host: str = "smtp.gmail.com"
#     smtp_port: int = 587
#     smtp_user: str = ""
#     smtp_password: str = ""
#     email_from: str = "noreply@presence.app"
    
#     # App
#     app_name: str = "Presence"
#     debug: bool = False
    
#     class Config:
#         env_file = ".env"


# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()


# settings = get_settings()
# chat gpt fixed deployment code
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Database (IMPORTANT FIX FOR RAILWAY)
    database_url: str = os.getenv("DATABASE_URL")

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "change-this-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Cloudinary
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # Email (SMTP)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    email_from: str = "noreply@presence.app"

    # App
    app_name: str = "Presence"
    debug: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()