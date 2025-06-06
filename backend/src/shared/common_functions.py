import base64

import cv2
import numpy as np
import zstandard as zstd
from httpx import Response
from jose import jwt, JWTError

from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import Role

logger = setup_logger(__name__)


def decode_token(token: str, is_refresh: bool = False) -> dict[str, any] | None:
    """
    Decode token
    :param token: Token for decode
    :param is_refresh: True if it is refresh token
    :return: dict[str, any] | None: Decoded token payload or None if error
    """
    try:
        if token == settings.api_key:
            return {"role": Role.SUPER_ADMIN.value, "sub": 12}
        payload = jwt.decode(token, settings.jwt_secret_refresh if is_refresh else settings.jwt_secret,
                             algorithms=settings.jwt_algorithm, options={"verify_exp": False})
        logger.info(f"Token decoded successfully: {payload}")
        return payload
    except JWTError as e:
        logger.warning(f"JWTError: {e}")
        return None


def verify_response(response: Response, waited_status_code: int = 200) -> dict[str, int | str] | None:
    """
    Verify response code
    :param response: Response to verify
    :param waited_status_code: Waited status code
    :return: Error if status code is not matched
    """
    if response.status_code != waited_status_code:
        try:
            detail = response.json().get("detail", "Unknown error")
        except Exception:
            detail = response.text or "Unknown error"
        logger.error(f"Response error: code - {response.status_code} detail - {detail}")
        return {"status_code": response.status_code, "detail": detail}
    logger.info(f"Verified response {response.json()} successfully")
    return None


dctx = zstd.ZstdDecompressor()
cctx = zstd.ZstdCompressor(level=3)
def decompress_image(compressed_bytes: bytes, read_regime = cv2.IMREAD_GRAYSCALE) -> np.ndarray:
    # 1. Decompress
    decompressed = dctx.decompress(compressed_bytes)
    logger.info("Decompressed image")
    # 2. Преобразование в numpy-изображение (если исходно это было изображение в формате .jpg/.png)
    image_array = np.frombuffer(decompressed, dtype=np.uint8)
    # 3. Декодирование в OpenCV-изображение (BGR)
    image = cv2.imdecode(image_array, read_regime)
    logger.info("Image shape: {}".format(image.shape))
    if image is None:
        raise ValueError("Failed to decode image")
    return image


def decode_base64_image(b64_str: str) -> np.ndarray:
    try:
        compressed_bytes = base64.b64decode(b64_str)
        return decompress_image(compressed_bytes)  # используем твою функцию
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise

def encode_image_to_base64(image: np.ndarray, format: str = ".jpg") -> str:
    # encode image to .jpg/.png format in memory
    success, buffer = cv2.imencode(format, image)
    if not success:
        raise ValueError("Failed to encode image to buffer")
    encoded = base64.b64encode(buffer).decode("utf-8")
    return encoded

def compress_image(image: 'np.ndarray') -> bytes:
    _, encoded = cv2.imencode('.jpg', image)
    return cctx.compress(encoded.tobytes())


def get_partition(camera_id: int, num_partitions: int) -> int:
    return hash(camera_id) % num_partitions