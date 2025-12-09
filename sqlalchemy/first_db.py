from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String
from pydantic import EmailStr

# Engine
engine = create_engine("sqlite+pysqlite:///sqlalchemy/db_1.db")
# Models
class Base(DeclarativeBase):
    pass

class UserBase(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))

Base.metadata.create_all(engine)
