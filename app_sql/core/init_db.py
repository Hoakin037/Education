from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import Optional
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker
    )

engine = create_async_engine("postgresql+asyncpg://postgres:fimoZNyiYe6an@localhost:5432/app_sql")

class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255))
    fullname: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(default=None)

async def init_db():
    """Создает все таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
