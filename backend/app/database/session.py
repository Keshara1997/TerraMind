
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# ==========================================
# SQLAlchemy Engine
# ==========================================

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    echo=settings.APP_DEBUG,
)


# ==========================================
# Session Factory
# ==========================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ==========================================
# Declarative Base
# ==========================================

class Base(DeclarativeBase):
    pass


# ==========================================
# Database Dependency
# ==========================================

def get_db():
    """
    Provide a database session to API endpoints.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# Database Health Check
# ==========================================

def check_database_connection() -> bool:
    """
    Check whether PostgreSQL is reachable.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return True

    except Exception:
        return False
