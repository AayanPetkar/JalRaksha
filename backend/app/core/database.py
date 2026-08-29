from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base  # single source of truth for model metadata

DATABASE_URL = settings.EFFECTIVE_DATABASE_URL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# SQLite needs check_same_thread=False since FastAPI may use the connection
# across different threads within a request/response cycle. This has no
# effect on the PostgreSQL/PostGIS production path.
connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

if IS_SQLITE:
    # Only import/activate the SQLite spatial compatibility shim when we are
    # actually running against SQLite. The PostgreSQL/PostGIS path is
    # untouched.
    from app.core.spatial_compat import install_sqlite_spatial_support
    install_sqlite_spatial_support(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
