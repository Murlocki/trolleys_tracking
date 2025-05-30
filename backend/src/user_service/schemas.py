from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, Field, AliasChoices

from src.user_service.models import Role


class UserData(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'firstName'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lastName'))
    email: EmailStr

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Role = Field(default=Role.SERVICE)
    user_data: UserData = Field(default=None, validation_alias=AliasChoices('user_data', 'userData'))



class UserUpdate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str | None = Field(None)
    is_active: bool = Field(False)
    version: int = Field(0)


class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)
