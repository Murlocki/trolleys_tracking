import cv2
import numpy as np
from ultralytics import YOLO

from src.classification_service.classification_settings import classification_settings
from src.classification_service.models.BasicModel import BasicClassificator

from src.shared.logger_setup import setup_logger
from src.shared.schemas import BoundingBox

logger = setup_logger(__name__)

class Yolo11Model(BasicClassificator):
    def classify(self, image, bounding_boxes: list[BoundingBox]) -> list[BoundingBox]:
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return bounding_boxes


    def __init__(self, model_path:str, parameters:dict):
        self.model = YOLO(model_path)
        self.parameters = parameters

yolo11_model = Yolo11Model(model_path=classification_settings.full_model_path,
                           parameters={
                               "imgsz":classification_settings.classification_yolo_11_img_sz
                           })

