import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "CRUD API"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/crud_db")
    _cors = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    CORS_ORIGINS: list[str] = [o.strip() for o in _cors.split(",") if o.strip()]


settings = Settings()
