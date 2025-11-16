"""
Database connection and session management using SQLAlchemy 2.0.
Includes async and sync session factories for PostgreSQL with TimescaleDB.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator, Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Sync engine for Alembic migrations and sync operations
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO,
)

# Async engine for FastAPI endpoints
# Convert postgresql:// to postgresql+asyncpg://
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DATABASE_ECHO,
)

# Session factories
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Enable PostGIS extension on connection
@event.listens_for(sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Enable PostGIS and TimescaleDB extensions on new connections."""
    with dbapi_conn.cursor() as cursor:
        # Check and enable PostGIS
        cursor.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'postgis'"
        )
        if not cursor.fetchone():
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
                logger.info("PostGIS extension enabled")
            except Exception as e:
                logger.warning(f"Could not enable PostGIS: {e}")

        # Check and enable TimescaleDB
        cursor.execute(
            "SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'"
        )
        if not cursor.fetchone():
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
                logger.info("TimescaleDB extension enabled")
            except Exception as e:
                logger.warning(f"Could not enable TimescaleDB: {e}")

        dbapi_conn.commit()


# Dependency for FastAPI endpoints (async)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Sync session context manager (for Celery tasks)
def get_sync_db() -> Generator[Session, None, None]:
    """
    Sync database session for Celery tasks and scripts.

    Usage:
        with get_sync_db() as db:
            items = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """Initialize database - create all tables."""
    from app.models.base import Base

    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        import app.models  # noqa

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """Close database connections."""
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")
