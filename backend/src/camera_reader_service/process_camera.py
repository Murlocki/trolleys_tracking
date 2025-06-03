from src.camera_reader_service.schemas import Status
from src.shared.logger_setup import setup_logger
from src.shared.schemas import CameraDTO
from src.shared.redis_base import redis_client

logger = setup_logger(__name__)

class CameraReaderManager:
    @staticmethod
    async def activate_camera(camera:CameraDTO):
        process_key = f"camera:{camera.id}"
        logger.info(f"Attempting to activate camera:{camera.id}")
        exist_process = await CameraReaderManager.get_camera_process(camera.id)
        if not exist_process:
            return True
    @staticmethod
    async def deactivate_camera(camera:CameraDTO):
        return True
    @staticmethod
    async def get_camera_status(camera:CameraDTO):
        try:
            logger.info(f"Attempting to get camera status:{camera.id}")
            exist_process = await CameraReaderManager.get_camera_process(camera.id)
            if not exist_process:
                logger.warning(f"Camera {camera.id} reader process not exist")
                return Status.not_active
            logger.info(f"Camera {camera.id} status: {exist_process.status}")
            return exist_process.status
        except Exception as e:
            logger.error(f"Camera {camera.id} reader process checking: {e}")
            raise

    @staticmethod
    async def get_camera_process(camera_id:int):
        existing_process = await redis_client.hgetall(f"camera:{camera_id}")
        logger.info(f"Existing process: {existing_process}")
        if not existing_process:
            return None
        return existing_process