from datetime import datetime

from sqlalchemy import UniqueConstraint

from typing import Optional

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.shared.database import Base
from src.shared.schemas import Role


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

    camera_associations: Mapped[list["CameraUserAssociation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CameraUserAssociation.camera_id",
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





class CameraGroup(Base):
    __tablename__ = 'camera_groups'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Уникальный идентификатор группы камер"
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="Название группы камер"
    )
    address: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Физический адрес расположения группы"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="Дополнительное описание группы"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания записи"
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
        comment="Версия записи для оптимистичной блокировки"
    )

    # Отношения
    cameras: Mapped[list["Camera"]] = relationship(
        "Camera",
        back_populates="camera_group",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Camera.id",
    )

    def __repr__(self):
        return f"CameraGroup(id={self.id}, name={self.name})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version
        }


class Camera(Base):
    __tablename__ = 'cameras'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Уникальный идентификатор камеры"
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="Название камеры"
    )
    address_link: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="Строка подключения к камере"
    )
    group_id: Mapped[int] = mapped_column(
        ForeignKey("camera_groups.id", ondelete="CASCADE"),
        nullable=False,
        comment="Ссылка на группу камер"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания записи"
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
        comment="Версия записи для оптимистичной блокировки"
    )

    # Отношения
    camera_group: Mapped["CameraGroup"] = relationship(
        "CameraGroup",
        back_populates="cameras",
        lazy="joined",
    )

    user_associations: Mapped[list["CameraUserAssociation"]] = relationship(
        back_populates="camera",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CameraUserAssociation.user_id",
    )

    def __repr__(self):
        return f"Camera(id={self.id}, name={self.name}, link={self.address_link})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address_link": self.address_link,
            "group_id": self.group_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "camera_group": self.camera_group.to_dict() if self.camera_group else None
        }


class CameraUserAssociation(Base):
    __tablename__ = 'camera_user_association'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="Суррогатный ключ"
    )
    camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('cameras.id')
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id')
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата создания записи"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата последнего обновления"
    )

    __table_args__ = (
        UniqueConstraint('camera_id', 'user_id', name='uq_camera_user'),
    )

    # Связи
    camera: Mapped["Camera"] = relationship(
        back_populates="user_associations",
        lazy="joined"
    )

    user: Mapped["User"] = relationship(
        back_populates="camera_associations",
        lazy="joined"
    )

    def __repr__(self):
        return f"CameraUserAssociation(id={self.id}, camera_id={self.camera_id}, user_id={self.user_id})"

    def to_dict(self):
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "camera": self.camera.to_dict() if self.camera else None,
            "user": self.user.to_dict() if self.user else None
        }