from src.detection_service.models.Yolo8Model import yolo8_model
from src.shared.schemas import DetectionRegime

models_dict = {
    DetectionRegime.yoloV8x: yolo8_model
}