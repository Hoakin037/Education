import sys
from typing import List, Optional

from sqlalchemy import String, ForeignKey, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)

# --- 1. Настройка движка (Engine) ---
# echo=True выводит все SQL-запросы в консоль (полезно для обучения)
engine = create_engine("sqlite:///db_2.db", echo=True) 


# --- 2. Объявление моделей (Declarative Models) ---

class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class User(Base):
    __tablename__ = "user_account"

    # Mapped[...] - это новая фишка 2.0. Она связывает тип Python с типом SQL.
    # mapped_column() используется для детальной настройки (PK, FK, nullable и т.д.)
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    
    # Optional[str], поле либо null либо строка
    fullname: Mapped[Optional[str]] 

    # Связь One-to-Many (Один User имеет много Address)
    # cascade="all, delete-orphan" означает: если удалить юзера, удалятся и его адреса
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    
    # Внешний ключ (Foreign Key)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    # Связь Many-to-One (Обратная ссылка на User)
    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email={self.email_address!r})"


# --- 3. Инициализация схемы БД ---
# Создает таблицы на основе унаследованных от Base классов
Base.metadata.create_all(engine)


# --- 4. Работа с данными (CRUD) ---

def run_example():
    # Открываем сессию. Контекстный менеджер сам закроет её в конце.
    with Session(engine) as session:
        
        print("\n--- CREATE (INSERT) ---")
        
        # Создаем пользователей
        spongebob = User(name="spongebob", fullname="Spongebob Squarepants")
        sandy = User(name="sandy", fullname="Sandy Cheeks")
        patrick = User(name="patrick") # fullname будет None

        # Добавляем адреса (ORM магия: не нужно вручную ставить user_id)
        spongebob.addresses.append(Address(email_address="spongebob@sqlalchemy.org"))
        sandy.addresses.append(Address(email_address="sandy@sqlalchemy.org"))
        sandy.addresses.append(Address(email_address="sandy@squirrel.com"))

        # Добавляем объекты в сессию
        session.add_all([spongebob, sandy, patrick])
        
        # Отправляем изменения в БД (COMMIT)
        session.commit()
        print("Данные успешно добавлены.")


        print("\n--- READ (SELECT) ---")

        # 1. Выбрать всех пользователей с именем "sandy"
        stmt = select(User).where(User.name == "sandy")
        # scalars() используется, когда мы хотим получить список ORM-объектов, а не кортежей
        user_sandy = session.scalars(stmt).first() 
        print(f"Найдена: {user_sandy}")
        
        # 2. Доступ к связанным данным (Lazy loading сработает автоматически при обращении)
        if user_sandy:
            print(f"Адреса Сэнди: {user_sandy.addresses}")


        print("\n--- UPDATE --- ")

        # Получаем Патрика
        patrick_obj = session.scalars(select(User).where(User.name == "patrick")).first()
        if patrick_obj:
            # Просто меняем атрибут
            patrick_obj.fullname = "Patrick Star"
            # При коммите SQLAlchemy увидит "грязный" (dirty) объект и сделает UPDATE
            session.commit()
            print(f"Обновлен: {patrick_obj}")


        print("\n--- DELETE ---")
        
        # Удаляем Спанчбоба
        spongebob_obj = session.scalars(select(User).where(User.name == "spongebob")).first()
        if spongebob_obj:
            session.delete(spongebob_obj)
            session.commit()
            print("Спанчбоб удален.")
            
        # Проверка каскадного удаления (адрес Спанчбоба тоже должен исчезнуть)
        orphaned_address = session.scalars(
            select(Address).where(Address.email_address == "spongebob@sqlalchemy.org")
        ).first()
        print(f"Адрес Спанчбоба в базе? {'Да' if orphaned_address else 'Нет (удален каскадно)'}")

if __name__ == "__main__":
    run_example()