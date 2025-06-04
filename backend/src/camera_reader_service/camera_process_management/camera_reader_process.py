import asyncio
import cv2
from src.camera_reader_service.schemas import Status
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client

logger = setup_logger(__name__)


def start_camera_reader(camera_id: int):
    """Функция, которая запускается в отдельном процессе"""
    asyncio.run(read_camera(camera_id))


def test_camera_connection(address_link: str) -> bool:
    cap = cv2.VideoCapture(0)
    result = cap.isOpened()
    cap.release()
    return result

def process_camera(cap: cv2.VideoCapture, frame_count: int) -> bool:
    ret, frame = cap.read()
    if not ret:
        return False

    # Обрабатываем каждый 5-й кадр
    if frame_count % 5 == 0:
        logger.info(f"[FRAME {frame_count}] ✅ Processed frame")

        # 🔧 здесь можно добавить обработку:
        # save_frame_to_disk_or_send(frame)

    return True

async def read_camera(camera_id: int):
    redis_key = f"camera:{camera_id}"
    logger.info(f"[{camera_id}] Starting camera reading process")

    cap = None
    try:
        camera_data = await redis_client.hgetall(redis_key)
        if not camera_data:
            logger.warning(f"[{camera_id}] No Redis data found.")
            return

        address_link = camera_data.get("address_link")
        if not address_link:
            logger.error(f"[{camera_id}] Camera address missing.")
            return

        logger.info(f"[{camera_id}] Camera address link: {address_link}")

        if not test_camera_connection(address_link):
            logger.error(f"[{camera_id}] Camera connection test failed.")
            return  # вызовет finally
        logger.info(f"[{camera_id}] Camera connection test passed")

        frame_count = 0
        cap = cv2.VideoCapture(0)
        while True:
            current_status = await redis_client.hget(redis_key, "status")
            if current_status != Status.is_active.value:
                logger.info(f"[{camera_id}] Stop flag detected. Exiting...")
                break

            frame_count += 1
            if frame_count % 5 == 0:
                if not process_camera(cap, frame_count):
                    logger.warning(f"[{camera_id}] process_camera failed.")
                    break

            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        logger.info(f"[{camera_id}] Cancelled")
    finally:
        if cap is not None:
            cap.release()
        await redis_client.delete(redis_key)
        logger.info(f"[{camera_id}] Process is finished")

