"""Create the PostgreSQL database (if missing) and all SQLAlchemy tables."""

from urllib.parse import urlparse

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401 — registers model metadata


def ensure_database_exists() -> None:
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip("/")
    if not db_name:
        raise ValueError("DATABASE_URL must include a database name")

    admin_url = parsed._replace(path="/postgres").geturl()
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    admin_engine.dispose()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def init_db() -> None:
    try:
        ensure_database_exists()
    except Exception:
        # Managed Postgres (e.g. Render): DB already exists / no CREATE privilege
        pass
    create_tables()
