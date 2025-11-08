"""
Database configuration and session management.

Uses SQLAlchemy async with PostgreSQL for optimal performance.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.config import settings

# Create async engine
# Convert DATABASE_URL from psycopg2 format to asyncpg format
# Remove ?sslmode=require and add connect_args for SSL
database_url = str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")
# Remove sslmode parameter (asyncpg doesn't support it in URL)
if "?sslmode=" in database_url:
    database_url = database_url.split("?sslmode=")[0]

engine = create_async_engine(
    database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    connect_args={"ssl": "require"},  # asyncpg SSL configuration
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session for request handling.

    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
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


async def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in models if they don't exist.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.

    Should be called on application shutdown.
    """
    await engine.dispose()
