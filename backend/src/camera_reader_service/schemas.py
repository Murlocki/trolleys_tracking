from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, AliasChoices
from pydantic.alias_generators import to_camel

from src.shared.schemas import DetectionRegime, ClassificationRegime, TrackingRegime


# Enum for camera active statuses
class Status(str,Enum):
    is_active = "active"
    not_active = "not_active"

class ActivationProps(BaseModel):
    detection_regime: DetectionRegime = Field(
        default=DetectionRegime.yoloV8x,
        description="Detection regime",
        validation_alias=AliasChoices('detection_regime', 'detectionRegime')
    )
    classification_regime: ClassificationRegime = Field(
        default=ClassificationRegime.yoloV8x,
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

class CameraProcess(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()), description="Process ID")
    camera_id: int = Field(description="Camera ID", validation_alias=AliasChoices('camera_id', 'cameraID'))
    address_link: str = Field(..., min_length=15, validation_alias=AliasChoices('address_link', 'addressLink'))
    status: Status = Field(default=Status.not_active)
    activation_props: ActivationProps = Field(default_factory=ActivationProps)

    class Config:
        alias_generator = to_camel
        from_attributes = True
        use_enum_values = True
