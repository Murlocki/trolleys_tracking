from datetime import datetime
from typing import Optional, Any, Generic, TypeVar

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



class UserData(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'firstName'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lastName'))
    email: EmailStr

class UserDTO(BaseModel):
    id: int
    username: str = Field(validation_alias=AliasChoices('username', 'userName'))
    is_active: bool = Field(False, validation_alias=AliasChoices('is_active', 'isActive'))
    role: str = Field("service", validation_alias=AliasChoices('role'))
    user_data: UserData | None = Field(None, validation_alias=AliasChoices('user_data', 'userData'))

    class Config:
        alias_generator = to_camel
        from_attributes = True




class UserAuthDTO(BaseModel):
    identifier: str
    password: str
