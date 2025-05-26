import asyncio
from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String, Boolean, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

from src.shared.database import engine, SessionLocal

Base = declarative_base()


class Role(Enum):
    SERVICE = "service"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

    @classmethod
    def get_display_name(cls, role):
        names = {
            cls.SERVICE: "Service Account",
            cls.ADMIN: "Administrator",
            cls.SUPER_ADMIN: "Super Administrator"
        }
        return names.get(role, "Unknown")


class UserData(Base):
    __tablename__ = 'user_data'
    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="user_data")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, index=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[Role] = mapped_column(SQLAlchemyEnum(Role), default=Role.SERVICE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_data: Mapped[UserData] = relationship("UserData", back_populates="user", uselist=False,
                                               cascade="all, delete-orphan", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_active": self.is_active,
            "role": self.role.value if self.role else None,
            "role_display": Role.get_display_name(self.role) if self.role else None,
            "email": self.user_data.email if self.user_data else None,
            "first_name": self.user_data.first_name if self.user_data else None,
            "last_name": self.user_data.last_name if self.user_data else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
        }


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def create_user_example():
    async with SessionLocal() as session:
        try:
            new_user = User(
                username="john_doe",
                hashed_password="hashed_password_123",
                is_active=True,
                role=Role.ADMIN,
                user_data=UserData(
                    email="john.doe@example.com",
                    first_name="John",
                    last_name="Doe",
                )
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            await session.refresh(new_user.user_data)
        except Exception as e:
            await session.rollback()
            print(f"Error creating user: {e}")
            raise
    print(f"Created user: {new_user.to_dict()}")


async def main():
    await init_db()
    await create_user_example()


if __name__ == "__main__":
    asyncio.run(main())
