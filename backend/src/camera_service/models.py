from datetime import datetime
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.shared.database import Base


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
    cameras: Mapped[List["Camera"]] = relationship(
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
    ip_address: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
        comment="IP-адрес камеры"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Флаг активности камеры"
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

    def __repr__(self):
        return f"Camera(id={self.id}, name={self.name}, ip={self.ip_address})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ip_address": self.ip_address,
            "is_active": self.is_active,
            "group_id": self.group_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "camera_group": self.camera_group.to_dict() if self.camera_group else None
        }