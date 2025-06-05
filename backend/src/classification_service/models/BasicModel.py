from abc import ABC, abstractmethod

from src.shared.schemas import BoundingBox


class BasicClassificator(ABC):
    @abstractmethod
    def classify(self, image, bounding_boxes: list[BoundingBox]) -> list[BoundingBox]:
        pass


