from abc import ABC, abstractmethod

from src.shared.schemas import BoundingBox


class BasicTracker(ABC):
    @abstractmethod
    def process_image(self, image, detections: list[BoundingBox])->list[BoundingBox]:
        pass


