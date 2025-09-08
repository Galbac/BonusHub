from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings

DATABASE_URL = settings.db_url

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
asyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with asyncSessionLocal() as session:
        yield session
