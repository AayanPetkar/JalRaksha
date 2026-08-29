import os
from pydantic_settings import BaseSettings
from typing import List

# Anchor for resolving relative SQLite paths so the demo database always
# resolves to the same file (backend/jalraksha_demo.db) regardless of the
# process's current working directory — e.g. `uvicorn` run from `backend/`,
# pytest run from the repo root, or `scripts/reset_demo.py` run from the
# repo root must all agree on one file.
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _resolve_sqlite_url(url: str) -> str:
    """Rewrite a relative sqlite:/// URL to an absolute path anchored at
    the backend directory, so it resolves to the same file no matter what
    the process's current working directory is. Absolute sqlite URLs and
    non-sqlite URLs are returned unchanged.
    """
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url
    raw_path = url[len(prefix):]
    if raw_path.startswith("/") or raw_path == ":memory:":
        return url  # already absolute, or an in-memory database
    absolute_path = os.path.normpath(os.path.join(_BACKEND_DIR, raw_path))
    return f"{prefix}{absolute_path}"

class Settings(BaseSettings):
    PROJECT_NAME: str = "JalRaksha - Flood Safety API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"
    DEMO_MODE: bool = True
    
    POSTGRES_DB: str = "jalraksha_db"
    POSTGRES_USER: str = "jalraksha_user"
    POSTGRES_PASSWORD: str = "change_this_secure_password"
    POSTGRES_HOST: str = "database"
    POSTGRES_PORT: int = 5432
    # Production / future PostgreSQL + PostGIS connection string. Left untouched
    # and unused for SIH demo runtime, but kept available for future use.
    DATABASE_URL: str = "postgresql://jalraksha_user:change_this_secure_password@database:5432/jalraksha_db"

    # SQLite connection string used for the SIH demo runtime when DEMO_MODE is
    # true. Requires no PostgreSQL/PostGIS/Docker to start.
    DEMO_DATABASE_URL: str = "sqlite:///./jalraksha_demo.db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    JWT_SECRET_KEY: str = "change_this_jwt_secret_key_to_a_long_random_string_32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    MAPBOX_ACCESS_TOKEN: str = "mock_mapbox_token"
    
    class Config:
        env_file = ".env"
        extra = "allow"

    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        """Database URL actually used at runtime.

        In DEMO_MODE, the backend always uses the local SQLite file so the
        SIH demo can start without PostgreSQL/PostGIS/Docker. DATABASE_URL
        (PostgreSQL/PostGIS) remains configured and available for future
        production use and is unaffected by demo mode.
        """
        if self.DEMO_MODE:
            return _resolve_sqlite_url(self.DEMO_DATABASE_URL)
        return self.DATABASE_URL

settings = Settings()
