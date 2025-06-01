from typing import Optional

from pydantic import BaseModel, Field, AliasChoices
from pydantic.alias_generators import to_camel

from src.shared.schemas import UserData
from src.shared.models import Role


class CameraGroupSchema(BaseModel):
    name: str = Field(alias="name", min_length=1)
    address: str | None= Field(default=None,alias="address", min_length=1)
    description: str | None= Field(alias="description", default=None)
    version: int = Field(alias="version", default=0)

class CameraGroupDTO(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name", min_length=1)
    address: str | None = Field(default=None, alias="address", min_length=1)
    description: str | None = Field(alias="description", default=None)
    version: int = Field(alias="version", default=0)

class CameraGroupAdminDTO(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name", min_length=1)
    address: str | None = Field(default=None, alias="address", min_length=1)
    description: str | None = Field(alias="description", default=None)
    version: int = Field(alias="version", default=0)
    created_at: str = Field(default="", validation_alias=AliasChoices('created_at', 'createdAt'))
    updated_at: str = Field(default="", validation_alias=AliasChoices('updated_at', 'updatedAt'))

    class Config:
        alias_generator = to_camel
        from_attributes = True



class CameraSchema(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name", min_length=1)
