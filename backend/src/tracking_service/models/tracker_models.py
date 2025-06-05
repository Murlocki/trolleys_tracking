from src.detection_service.models.Yolo11Model import yolo11_model
from src.shared.schemas import DetectionRegime, TrackingRegime
from src.tracking_service.models.DeepsortModel import deepsorter

models_dict = {
    TrackingRegime.deepsort: deepsorter
}