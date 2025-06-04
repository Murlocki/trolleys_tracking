import cv2
import numpy as np
from ultralytics import YOLO
import zstandard as zstd
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

def compress_image_with_zstd(image_path: str, compression_level: int = 10) -> bytes:
    # 1. Чтение изображения
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # 2. Кодирование изображения в JPEG (или можно в .png — cv2.IMWRITE_PNG_COMPRESSION)
    success, encoded_image = cv2.imencode(".jpg", image)
    if not success:
        raise ValueError("Failed to encode image to JPEG")

    # 3. Сжатие Zstandard
    compressor = zstd.ZstdCompressor(level=compression_level)
    compressed = compressor.compress(encoded_image.tobytes())

    return compressed
def decompress_image(compressed_bytes: bytes) -> np.ndarray:
    # 1. Декомпрессия
    dctx = zstd.ZstdDecompressor()
    decompressed = dctx.decompress(compressed_bytes)

    # 2. Преобразование в numpy-изображение (если исходно это было изображение в формате .jpg/.png)
    image_array = np.frombuffer(decompressed, dtype=np.uint8)

    # 3. Декодирование в OpenCV-изображение (BGR)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image")

    return image

image = cv2.imread(r"C:\Users\kirill\Desktop\diploma\trolleys_tracking\backend\src\detection_service\weights\-_PNG.rf.54fb6638f78167f07b15ff473c798b95.jpg")
compress = compress_image_with_zstd(r"C:\Users\kirill\Desktop\diploma\trolleys_tracking\backend\src\detection_service\weights\-_PNG.rf.54fb6638f78167f07b15ff473c798b95.jpg")

img = decompress_image(compress)

result = yolo11_model.process_image(img)
print(result)
print(yolo11_model.process_bounding_box(result))
