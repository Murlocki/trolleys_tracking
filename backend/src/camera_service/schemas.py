from pydantic import BaseModel, Field, AliasChoices
from pydantic.alias_generators import to_camel


class CameraGroupSchema(BaseModel):
    name: str = Field(alias="name", min_length=1)
    address: str | None = Field(default=None, alias="address", min_length=1)
    description: str | None = Field(alias="description", default=None)
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
    name: str = Field(alias="name", min_length=1)
    address_link: str = Field(validation_alias=AliasChoices('address_link', 'addressLink'), min_length=1)
    group_id: int = Field(default=0, validation_alias=AliasChoices('group_id', 'groupId'))
    version: int = Field(alias="version", default=0)

    class Config:
        alias_generator = to_camel
        from_attributes = True


class CameraAdminDTO(BaseModel):
    id: int = Field(alias="id")
    name: str = Field(alias="name")
    address_link: str = Field(validation_alias=AliasChoices('address_link', 'addressLink'), min_length=1)
    group_id: int = Field(default=0, validation_alias=AliasChoices('group_id', 'groupId'))
    version: int = Field(alias="version", default=0)
    created_at: str = Field(default="", validation_alias=AliasChoices('created_at', 'createdAt'))
    updated_at: str = Field(default="", validation_alias=AliasChoices('updated_at', 'updatedAt'))

    class Config:
        alias_generator = to_camel
        from_attributes = True


class CameraUserAssociationSchema(BaseModel):
    camera_id: int = Field(validation_alias=AliasChoices('camera_id', 'cameraId'))
    user_id: int = Field(default=0, validation_alias=AliasChoices('user_id', 'userId'))
    version: int = Field(alias="version", default=0)

    class Config:
        alias_generator = to_camel
        from_attributes = True


class CameraUserAssociationDTO(BaseModel):
    id: int = Field(alias="id")
    camera_id: int = Field(validation_alias=AliasChoices('camera_id', 'cameraId'))
    user_id: int = Field(default=0, validation_alias=AliasChoices('user_id', 'userId'))

    class Config:
        alias_generator = to_camel
        from_attributes = True


class CameraUserAssociationAdminDTO(BaseModel):
    id: int = Field(alias="id")
    camera_id: int = Field(validation_alias=AliasChoices('camera_id', 'cameraId'))
    camera_name: str = Field(validation_alias=AliasChoices('camera_name', 'cameraName'))
    user_id: int = Field(default=0, validation_alias=AliasChoices('user_id', 'userId'))
    user_name: str = Field(validation_alias=AliasChoices('user_name', 'userName'))
    created_at: str = Field(default="", validation_alias=AliasChoices('created_at', 'createdAt'))
    updated_at: str = Field(default="", validation_alias=AliasChoices('updated_at', 'updatedAt'))

    class Config:
        alias_generator = to_camel
        from_attributes = True
