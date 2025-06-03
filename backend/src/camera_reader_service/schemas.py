from enum import Enum

from pydantic import BaseModel, Field, AliasChoices
from pydantic.alias_generators import to_camel


# Enum for camera active statuses
class Status(Enum):
    is_active = "active"
    not_active = "not_active"


class CameraProcess(BaseModel):
    id: str = Field(description="Process ID", )
    camera_id: int = Field(description="Camera ID", validation_alias=AliasChoices('camera_id', 'cameraID'))
    address_link: str = Field(validation_alias=AliasChoices('address_link', 'addressLink'), min_length=15)
    status: Status = Field(Status.not_active)

    class Config:
        alias_generator = to_camel
        from_attributes = True
        use_enum_values = True
