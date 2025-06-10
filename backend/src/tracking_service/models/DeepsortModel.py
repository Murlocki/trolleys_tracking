from deep_sort_realtime.deep_sort.detection import Detection
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO

from src.detection_service.detection_settings import detection_settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import BoundingBox
from src.tracking_service.models.BasicTracker import BasicTracker

logger = setup_logger(__name__)


class DeepsortModel(BasicTracker):

    def process_image(self, image, detections: list[BoundingBox]) -> list[BoundingBox]:
        try:
            results = detections
            ds_detections = []
            for d in detections:
                x1, y1, x2, y2 = d.x, d.y, d.x + d.width, d.y + d.height
                bbox = ([x1, y1, x2 - x1, y2 - y1], 1, 0)  # DeepSort обычно принимает bbox в формате [x, y, w, h]
                ds_detections.append(bbox)  # confidence можно подставить реальный, если есть

            tracks = self.tracker.update_tracks(ds_detections, frame=image)
            logger.info(tracks)
            ds_detections = []
            for track in tracks:
                track_id = track.track_id
                ltrb = track.to_ltrb()
                x1, y1, x2, y2 = map(int, ltrb)
                ds_detections.append(BoundingBox(
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1,
                    id=track_id,
                ))
            logger.info(f"Processed {len(ds_detections)} detections")
            return ds_detections
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return []
    def __init__(self, parameters: dict):
        self.tracker = DeepSort(
            **parameters
        )
        self.parameters = parameters

parameters = {}
