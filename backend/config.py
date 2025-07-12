
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:rv@localhost/skillswap")
    clerk_secret_key: str = os.getenv("CLERK_SECRET_KEY", "")
    clerk_publishable_key: str = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

@lru_cache()
def get_settings():
    return Settings()
