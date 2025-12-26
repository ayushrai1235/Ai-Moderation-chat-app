from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    GEMINI_API_KEY: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    class Config:

        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
