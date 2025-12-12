from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import Optional
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker
    )

engine = create_async_engine("postgresql+asyncpg://localhostapp_sql/db/database.db")

class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass

class User(Base):
    __tablename__ = "Users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(255))
    fullname: Mapped[Optional[str]]
    is_active: Mapped[bool] = mapped_column(default=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(default=None)

def init_db():
    Base.metadata.create_all(engine)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session_maker() as session:
        yield session
