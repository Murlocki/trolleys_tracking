import asyncio
from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

from src.shared.database import engine, SessionLocal, Base
from src.shared.schemas import Role

from datetime import datetime
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from enum import Enum




class UserData(Base):
    __tablename__ = 'user_data'

    id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Совпадает с ID пользователя"
    )
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Имя пользователя"
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Фамилия пользователя"
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        comment="Email пользователя (уникальный)"
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Номер телефона"
    )

    # Отношения
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_data",
        single_parent=True
    )

    def to_dict(self) -> dict:
        """Сериализация в словарь"""
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }

    def __repr__(self):
        return f"UserData(id={self.id}, email={self.email})"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Уникальный идентификатор пользователя"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        unique=True,
        comment="Уникальное имя пользователя"
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хеш пароля пользователя"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Флаг активности аккаунта"
    )
    role: Mapped[Role] = mapped_column(
        SQLAlchemyEnum(Role),
        default=Role.SERVICE,
        nullable=False,
        comment="Роль пользователя"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания аккаунта"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата последнего обновления"
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Версия для оптимистичной блокировки"
    )

    # Отношения
    user_data: Mapped[Optional["UserData"]] = relationship(
        "UserData",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def to_dict(self) -> dict:
        """Сериализация в словарь с вложенными данными"""
        data = {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "role": self.role.value if self.role else None,
            "role_display": Role.get_display_name(self.role) if self.role else None,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None,
            "version": self.version,
        }

        if self.user_data:
            data.update(self.user_data.to_dict())

        return data

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, role={self.role.value})"






async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)




async def main():
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
