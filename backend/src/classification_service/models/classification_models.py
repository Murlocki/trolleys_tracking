from src.classification_service.models.Yolo11Model import yolo11_model
from src.shared.schemas import DetectionRegime

models_dict = {
    DetectionRegime.yoloV11: yolo11_model,
    DetectionRegime.yoloV8x: None,
    DetectionRegime.yoloV9x: None,
}