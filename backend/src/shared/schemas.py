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
        session_id: str = Field(..., description="Unique identifier for the session", validation_alias=AliasChoices('session_id', 'sessionId'))
        user_id: int = Field(..., description="ID of the user associated with the session", validation_alias=AliasChoices('user_id', 'userId'))
        access_token: str = Field(..., description="Access token for the session", validation_alias=AliasChoices('access_token', 'accessToken'))
        refresh_token: str | None = Field(None, description="Refresh token for the session", validation_alias=AliasChoices('refresh_token', 'refreshToken'))
        device: str = Field("unknown")
        ip_address: str = Field("unknown", validation_alias=AliasChoices('ip_address', 'ipAddress'))
        created_at: datetime = Field(datetime.now(), validation_alias=AliasChoices('created_at', 'createdAt'))
        expires_at: datetime = Field(datetime.now(), validation_alias=AliasChoices('expires_at', 'expiresAt'))

        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat(),  # Преобразование datetime в ISO строку
            }
            alias_generator = to_camel


class TokenModelResponse(BaseModel):
    token: str
    identifier: str | None


class AccessTokenUpdate(BaseModel):
    old_access_token: str
    new_access_token: str


T = TypeVar("T")


class AuthResponse(BaseModel, Generic[T]):
    token: Optional[str] = None
    data: Optional[T] = None


class PaginatorList(BaseModel, Generic[T]):
    page: int = Field(1)
    page_count: int = Field(1, validation_alias=AliasChoices('page_count', 'pageCount'))
    items_per_page: int = Field(10, validation_alias=AliasChoices('items_per_page', 'itemsPerPage'))
    item_count: int = Field(1, validation_alias=AliasChoices('item_count', 'itemCount'))
    items: List[T] = Field(default_factory=lambda: list)
    class Config:
        alias_generator = to_camel
        from_attributes = True

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
    version: int = Field(0, validation_alias=AliasChoices('version'))
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
    address_link: str = Field(validation_alias=AliasChoices('address_link', 'addressLink'), min_length=1)
    group_id: int = Field(validation_alias=AliasChoices('group_id', 'groupId'))
    version: int = Field(alias="version", default=0)

    class Config:
        alias_generator = to_camel
        from_attributes = True


class DetectionRegime(str,Enum):
    yoloV8x: str = "yoloV8x",
    yoloV9x: str = "yoloV9x",
    yoloV11: str = "yoloV11",

class ClassificationRegime(str,Enum):
    ResNet: str = "ResNet",

class TrackingRegime(str,Enum):
    deepsort: str = "deepsort"

class ActivationProps(BaseModel):
    detection_regime: DetectionRegime = Field(
        default=DetectionRegime.yoloV8x,
        description="Detection regime",
        validation_alias=AliasChoices('detection_regime', 'detectionRegime')
    )
    classification_regime: ClassificationRegime = Field(
        default=ClassificationRegime.ResNet,
        description = "Classification regime",
        validation_alias = AliasChoices('classification_regime', 'classificationRegime')
    )
    tracking_regime: TrackingRegime = Field(
        default=TrackingRegime.deepsort,
        description="Tracking regime",
        validation_alias=AliasChoices('tracking_regime', 'trackingRegime')
    )
    class Config:
        alias_generator = to_camel
        from_attributes = True
        use_enum_values = True


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    id: Optional[int] = None


class ImageMessage(BaseModel):
    camera_id: int = Field(..., validation_alias=AliasChoices('camera_id', 'cameraId'))
    timestamp: int
    meta: str
    image: bytes
    activation_props: ActivationProps = Field(..., validation_alias=AliasChoices('activation_props', 'activationProps'))
    bounding_boxes: List[BoundingBox] = Field(default_factory=list, validation_alias=AliasChoices('bounding_boxes', 'boundingBoxes'))

    class Config:
        use_enum_values = True
        alias_generator = to_camel
        from_attributes = True