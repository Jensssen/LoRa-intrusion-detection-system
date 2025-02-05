from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel import create_engine, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.src.config import Config

engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True
    )
)


async def init_db() -> None:
    async with engine.begin() as conn:
        statement = text("SELECT 'hello';")
        result = await conn.execute(statement)
        print(result.all())
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with Session() as session:
        yield session
