from pydantic_settings import BaseSettings
from typing import List

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
    DATABASE_URL: str = "postgresql://jalraksha_user:change_this_secure_password@database:5432/jalraksha_db"
    
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    JWT_SECRET_KEY: str = "change_this_jwt_secret_key_to_a_long_random_string_32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
    
    MAPBOX_ACCESS_TOKEN: str = "mock_mapbox_token"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
