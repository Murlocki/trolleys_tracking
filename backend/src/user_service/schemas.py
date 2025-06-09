from typing import Optional

from pydantic import BaseModel, Field, AliasChoices
from pydantic.alias_generators import to_camel

from src.shared.models import Role
from src.shared.schemas import UserData


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Role = Field(default=Role.SERVICE)
    user_data: UserData = Field(default=None, validation_alias=AliasChoices('user_data', 'userData'))

    class Config:
        alias_generator = to_camel
        from_attributes = True


class UserAdminDTO(BaseModel):
    id: int = Field(default=None)
    username: str = Field(min_length=3, max_length=50)
    role_display: str = Field(default=Role.get_display_name(Role.SERVICE),
                              validation_alias=AliasChoices('role_display', 'roleDisplay'))
    role: str = Field(default=Role.SERVICE)
    is_active: bool = Field(default=True, validation_alias=AliasChoices('is_active', 'isActive'))
    first_name: str | None = Field(default=None, min_length=3, max_length=50, validation_alias=AliasChoices('first_name', 'firstName'))
    last_name: str | None = Field(default=None, min_length=3, max_length=50, validation_alias=AliasChoices('last_name', 'lastName'))
    email: str | None = Field(default=None, validation_alias=AliasChoices('email'))
    created_at: str = Field(default="", validation_alias=AliasChoices('created_at', 'createdAt'))
    updated_at: str = Field(default="", validation_alias=AliasChoices('updated_at', 'updatedAt'))

    class Config:
        alias_generator = to_camel
        from_attributes = True


class UserUpdate(BaseModel):
    username: str
    role: Role = Field(default=Role.SERVICE)
    is_active: bool = Field(default=True, validation_alias=AliasChoices('is_active', 'isActive'))
    user_data: UserData | None = Field(default=None, validation_alias=AliasChoices('user_data', 'userData'))
    version: int = Field(0)


class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)


class PasswordForm(BaseModel):
    new_password: str = Field(min_length=8, validation_alias=AliasChoices('new_password', 'newPassword'))
    user_version: int = Field(default=0)
