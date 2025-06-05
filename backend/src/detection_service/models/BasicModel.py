from abc import ABC, abstractmethod

from src.shared.schemas import BoundingBox


class BasicModel(ABC):
    @abstractmethod
    def process_image(self, image):
        pass

    @abstractmethod
    def process_bounding_box(self, prediction) -> list[BoundingBox]:
        pass

