from datetime import datetime
from enum import Enum
from typing import Optional, Generic, TypeVar, List

from pydantic import BaseModel, Field, AliasChoices, EmailStr
from pydantic.alias_generators import to_camel


class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)


class SessionSchema(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str | None = Field(None)
    device: str = Field("unknown")
    ip_address: str = Field("unknown")


class SessionDTO(BaseModel):
    session_id: str
    user_id: int
    access_token: str
    refresh_token: str | None = None
    device: str = Field("unknown")
    ip_address: str = Field("unknown")
    created_at: datetime = Field(datetime.now())
    expires_at: datetime = Field(datetime.now())

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # Преобразование datetime в ISO строку
        }


class TokenModelResponse(BaseModel):
    token: str


class AccessTokenUpdate(BaseModel):
    old_access_token: str
    new_access_token: str

T = TypeVar("T")
class AuthResponse(BaseModel, Generic[T]):
    token: Optional[str] = None
    data: Optional[T] = None


class PaginatorList(BaseModel,Generic[T]):
    page: int = Field(1)
    page_count: int = Field(1)
    items_per_page: int = Field(10)
    item_count: int = Field(1)
    items: List[T] = Field(default_factory=lambda :list)

class UserData(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'firstName'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lastName'))
    email: EmailStr
    class Config:
        alias_generator = to_camel
        from_attributes = True


class UserDTO(BaseModel):
    id: int
    username: str = Field(validation_alias=AliasChoices('username', 'userName'))
    is_active: bool = Field(False, validation_alias=AliasChoices('is_active', 'isActive'))
    role: str = Field("service", validation_alias=AliasChoices('role'))
    user_data: UserData | None = Field(None, validation_alias=AliasChoices('user_data', 'userData'))

    class Config:
        alias_generator = to_camel
        from_attributes = True

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

    def level(self):
        levels = {
            Role.SERVICE: 1,
            Role.ADMIN: 2,
            Role.SUPER_ADMIN: 3,
        }
        return levels[self]

class UserAuthDTO(BaseModel):
    identifier: str
    password: str

class CameraDTO(BaseModel):
    id: int
    name: str = Field(alias="name", min_length=1)
    address_link: str = Field(validation_alias=AliasChoices('address_link', 'addressLink'), min_length=15)
    group_id: int = Field(validation_alias=AliasChoices('group_id', 'groupId'))
    is_active: bool = Field(default=False, validation_alias=AliasChoices('is_active', 'isActive'))
    version: int = Field(alias="version", default=0)

    class Config:
        alias_generator = to_camel
        from_attributes = True