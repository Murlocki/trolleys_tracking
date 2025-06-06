from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO

from src.detection_service.detection_settings import detection_settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import BoundingBox
from src.tracking_service.models.BasicTracker import BasicTracker

logger = setup_logger(__name__)


class DeepsortModel(BasicTracker):
    def process_image(self, image, detections: list[BoundingBox]) -> list[BoundingBox]:
        return detections

    def __init__(self, parameters: dict):
        self.tracker = DeepSort(
            **parameters
        )
        self.parameters = parameters

parameters = {}
