import asyncio

from src.camera_reader_service.schemas import Status
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client

logger = setup_logger(__name__)


def start_camera_reader(camera_id: int):
    """Функция, которая запускается в отдельном процессе"""
    asyncio.run(read_camera(camera_id))


async def read_camera(camera_id: int):
    redis_key = f"camera:{camera_id}"
    logger.info(f"[{camera_id}] Starting camera reading process")

    camera_data = await redis_client.hgetall(redis_key)
    if not camera_data:
        logger.warning(f"[{camera_id}] No Redis data found.")
        return

    address_link = camera_data.get("address_link")
    if not address_link:
        logger.error(f"[{camera_id}] Camera address missing.")
        return

    try:
        while True:
            current_status = await redis_client.hget(redis_key, "status")
            logger.info(f"[{camera_id}] Current status: {current_status}")
            if current_status != Status.is_active.value:
                logger.info(f"[{camera_id}] Stop flag detected. Exiting...")
                break

            logger.debug(f"[{camera_id}] Simulating frame read")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info(f"[{camera_id}] Cancelled")
    finally:
        logger.info(f"[{camera_id}] Cleaning up")
        await redis_client.delete(redis_key)
        logger.info(f"[{camera_id}] process is finished")
