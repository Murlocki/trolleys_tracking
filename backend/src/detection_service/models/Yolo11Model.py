from ultralytics import YOLO
from ultralytics.engine.results import Results

from src.detection_service.detection_settings import detection_settings
from src.detection_service.models.BasicModel import BasicModel
from src.shared.logger_setup import setup_logger
from src.shared.schemas import BoundingBox

logger = setup_logger(__name__)

class Yolo11Model(BasicModel):
    def process_bounding_box(self, prediction:  list[Results]) -> list[BoundingBox] | None:
        if prediction:
            boxes = prediction[0].boxes.xywh
            result_boxes = []
            for i,box in enumerate(boxes):
                bounding_box = BoundingBox(
                    x=box[0],
                    y=box[1],
                    width=box[2],
                    height=box[3],
                )
                result_boxes.append(bounding_box)
            return result_boxes
        return None

    def process_image(self, image) ->  list[Results]:
        logger.info("Processing image")
        return self.model.predict(image, **self.parameters, save=True)

    def __init__(self, model_path:str, parameters:dict):
        self.model = YOLO(model_path)
        self.parameters = parameters

yolo11_model = Yolo11Model(model_path=detection_settings.full_model_path,
                           parameters={
                               "imgsz":detection_settings.detection_yolo_11_img_sz,
                               "conf":detection_settings.detection_yolo_11_conf,
                               "iou":detection_settings.detection_yolo_11_iou,
                           })

