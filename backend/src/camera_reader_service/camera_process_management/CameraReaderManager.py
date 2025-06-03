import asyncio
import multiprocessing
import time
from datetime import timedelta
from uuid import uuid4

from src.camera_reader_service.camera_process_management.camera_reader_process import start_camera_reader
from src.camera_reader_service.schemas import Status, CameraProcess
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client
from src.shared.schemas import CameraDTO

logger = setup_logger(__name__)


class CameraReaderManager:

    @staticmethod
    async def activate_camera(camera: CameraDTO):
        logger.info(f"Activating camera {camera.id}")
        camera_status = await CameraReaderManager.get_camera_status(camera)

        if camera_status != Status.not_active:
            logger.warning(f"Camera {camera.id} already active")
            return None

        process_record = await CameraReaderManager.create_camera_process_record(camera)
        logger.info(f"Camera {camera.id} process record {process_record}")
        process = multiprocessing.Process(target=start_camera_reader, args=(camera.id,))
        process.start()

        logger.info(f"Camera {camera.id} started in PID {process.pid}")
        return process_record

    @staticmethod
    async def deactivate_camera(camera: CameraDTO):
        process_record = await CameraReaderManager.get_camera_process_record(camera.id)
        if process_record is None:
            logger.error(f"Camera {camera.id} not active")
            return None
        process_record.status = Status.not_active.value
        await redis_client.hset(f"camera:{camera.id}", mapping=process_record.model_dump())
        expire_seconds = int(timedelta(
            seconds=settings.camera_process_record_expire_seconds,
            minutes=settings.camera_process_record_expire_minutes,
            hours=settings.camera_process_record_expire_hours
        ).total_seconds())
        await redis_client.expire(f"camera:{camera.id}", expire_seconds)

        timeout = expire_seconds + 5  # немного больше, чем TTL
        start = time.monotonic()

        while True:
            process_record_check = await CameraReaderManager.get_camera_process_record(camera.id)
            if process_record_check is None:
                break

            if time.monotonic() - start > timeout:
                logger.warning(f"Camera {camera.id} process record still exists after timeout")
                break

            await asyncio.sleep(settings.camera_process_record_check_seconds)
        logger.info(f"Camera {camera.id} process was deactivated")
        return process_record



    @staticmethod
    async def get_camera_status(camera: CameraDTO):
        existing = await redis_client.hgetall(f"camera:{camera.id}")
        return Status(existing.get("status", Status.not_active.value))

    @staticmethod
    async def create_camera_process_record(camera: CameraDTO) -> CameraProcess:
        process_record = CameraProcess(
            id=str(uuid4()),
            camera_id=camera.id,
            address_link=camera.address_link,
            status=Status.is_active.value,
        )
        await redis_client.hset(f"camera:{camera.id}", mapping=process_record.model_dump())
        expire_seconds = int(timedelta(
            seconds=settings.camera_process_record_expire_seconds,
            minutes=settings.camera_process_record_expire_minutes,
            hours=settings.camera_process_record_expire_hours
        ).total_seconds())
        await redis_client.expire(f"camera:{camera.id}", expire_seconds)
        return process_record

    @staticmethod
    async def get_camera_process_record(camera_id) -> CameraProcess | None:
        result = await redis_client.hgetall(f"camera:{camera_id}")
        if not result:
            logger.error(f"Camera process for {camera_id} not found")
            return None
        logger.info(f"Camera {camera_id} process record {result}")
        return CameraProcess(
            id = result["id"],
            camera_id = result["camera_id"],
            address_link = result["address_link"],
            status = result["status"],
        )
