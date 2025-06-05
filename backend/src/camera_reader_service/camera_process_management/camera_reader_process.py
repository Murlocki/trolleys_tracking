import asyncio
import json
from datetime import timedelta

import cv2
import zstandard as zstd

from src.camera_reader_service.camera_process_management.cameraProducer import produce_async
from src.camera_reader_service.schemas import Status
from src.shared.common_functions import compress_image, get_partition
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client
from src.shared.schemas import ImageMessage, ActivationProps, DetectionRegime, ClassificationRegime, TrackingRegime

logger = setup_logger(__name__)


def start_camera_reader(camera_id: int):
    logger.info(f"Starting camera reader {camera_id}")
    asyncio.run(read_camera(camera_id))

def local_string(address_link):
    if address_link.isdigit():
        return int(address_link)
    return address_link

def test_camera_connection(address_link: str) -> bool:
    logger.info(f"Connecting to {address_link}")
    cap = cv2.VideoCapture(local_string(address_link))
    result = cap.isOpened()
    logger.info(f"Camera connection result: {result}")
    cap.release()
    return result

async def read_camera(camera_id: int):
    cap = None
    redis_key = None
    try:
        redis_key = f"camera:{camera_id}"
        logger.info(f"[{camera_id}] Starting camera reading process")

        camera_data = await redis_client.hgetall(redis_key)
        if not camera_data:
            logger.warning(f"[{camera_id}] No Redis data found.")
            return
        logger.info(f"[{camera_id}] Redis data found: {camera_data}")

        address_link = camera_data.get("address_link")
        if not address_link:
            logger.error(f"[{camera_id}] Camera address missing.")
            return
        logger.info(f"[{camera_id}] Camera address link: {address_link}")



        if not test_camera_connection(address_link):
            logger.error(f"[{camera_id}] Camera connection test failed.")
            return
        logger.info(f"[{camera_id}] Camera connection test passed")

        cap = cv2.VideoCapture(local_string(address_link))
        frame_count = 0
        ttl_seconds = timedelta(
            seconds=settings.camera_process_record_expire_seconds,
            minutes=settings.camera_process_record_expire_minutes,
            hours=settings.camera_process_record_expire_hours
        ).total_seconds()
        partition = get_partition(camera_id, settings.kafka_send_image_topic_partitions_count)
        logger.info(f"[{camera_id}] Partition: {partition}")

        # Pydantic модель пропсов режимов
        activation_props = camera_data.get("activation_props")
        props_dict = json.loads(activation_props)
        activation_props = ActivationProps(**props_dict)

        while True:
            current_status = await redis_client.hget(redis_key, "status")
            if current_status != Status.is_active.value:
                logger.info(f"[{camera_id}] Stop flag detected. Exiting...")
                break
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"[{camera_id}] Failed to read frame.")
                break
            frame_count += 1
            await redis_client.expire(redis_key, int(ttl_seconds))

            if frame_count % settings.camera_process_frame_skip == 0:
                compressed = compress_image(frame)
                logger.info(f"[{camera_id}] Compressed: {len(compressed)}")
                message = ImageMessage(
                    camera_id=camera_id,
                    timestamp=int(ttl_seconds),
                    meta=f"frame {frame_count}",
                    image=compressed,
                    activation_props=ActivationProps(
                        detection_regime=activation_props.detection_regime,
                        classification_regime=activation_props.classification_regime,
                        tracking_regime=activation_props.tracking_regime
                    )
                )

                await produce_async(message, partition=partition)
                logger.info(f"{camera_id} Produced message")
            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        logger.info(f"[{camera_id}] Cancelled")
    finally:
        if cap is not None: cap.release()
        if redis_key: await redis_client.delete(redis_key)
        logger.info(f"[{camera_id}] Process is finished")
