from src.detection_service.models.Yolo11Model import yolo11_model
from src.shared.schemas import DetectionRegime, TrackingRegime
from src.tracking_service.models.DeepsortModel import DeepsortModel, parameters

models_dict = {
    TrackingRegime.deepsort: DeepsortModel
}
models_params_dict = {
    TrackingRegime.deepsort: parameters
}