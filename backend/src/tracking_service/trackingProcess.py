from datetime import timedelta
import asyncio
from multiprocessing import Process, Queue
from aiokafka import AIOKafkaProducer

from src.shared.common_functions import decompress_image
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client
from src.shared.schemas import ImageMessage
from src.tracking_service.kafka_producer import produce_message
from src.tracking_service.models.BasicTracker import BasicTracker
from src.tracking_service.models.DeepsortModel import parameters
from src.tracking_service.models.tracker_models import models_dict, models_params_dict
from src.tracking_service.tracking_settings import tracking_settings

logger = setup_logger(__name__)

camera_queues = {}
camera_processes = {}

ttl = int(timedelta(
    seconds=tracking_settings.tracking_process_live_seconds,
    minutes=tracking_settings.tracking_process_live_minutes,
    hours=tracking_settings.tracking_process_live_hours
).total_seconds())


def get_redis_key(camera_id):
    return f"tracking_process:{camera_id}"


async def mark_camera_alive(camera_id):
    key = get_redis_key(camera_id)
    result = await redis_client.set(key, "alive", ex=ttl)
    logger.info(f"[REDIS] Set key {key}, TTL: {ttl}s (result: {result})")


async def is_camera_alive(camera_id):
    return await redis_client.exists(get_redis_key(camera_id)) == 1


def tracking_loop(camera_id, queue: Queue):
    asyncio.run(async_tracking_loop(camera_id, queue))

class SingletonTracker:
    _tracker_instance = None

    @staticmethod
    def get_tracker(tracker_class, *args, **kwargs):
        """
        Возвращает единственный экземпляр трекера. Если он ещё не создан — создаёт.
        :param tracker_class: класс трекера
        :param args: позиционные аргументы конструктора
        :param kwargs: именованные аргументы конструктора
        :return: трекер
        """
        if SingletonTracker._tracker_instance is None:
            SingletonTracker._tracker_instance = tracker_class(*args, **kwargs)
        return SingletonTracker._tracker_instance

    @staticmethod
    def reset():
        """Удаляет текущий экземпляр трекера (если нужно пересоздать вручную)."""
        SingletonTracker._tracker_instance = None



async def async_tracking_loop(camera_id, queue: Queue):
    logger.info(f"[TRACKER] Started for camera {camera_id}")
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_broker)
    await producer.start()
    logger.info(f"[TRACKER] Kafka producer started")

    await mark_camera_alive(camera_id)

    try:
        while True:
            alive = await is_camera_alive(camera_id)
            if not alive:
                logger.info(f"[TRACKER] No activity for camera {camera_id}, exiting")
                break

            try:
                data_dict = queue.get(timeout=5)
                data = ImageMessage.model_validate(data_dict)
            except Exception:
                continue

            await mark_camera_alive(camera_id)
            logger.info(f"[TRACKER] Processing frame")

            image = decompress_image(data.image)
            model: BasicTracker = SingletonTracker.get_tracker(
                tracker_class=models_dict.get(data.activation_props.tracking_regime),
                parameters=models_params_dict.get(data.activation_props.tracking_regime)
            )
            logger.info(f"Tracker obtained: f{model}")
            results = model.process_image(image, data.bounding_boxes)
            data.bounding_boxes = results

            await produce_message(data, producer)
            logger.info(f"[TRACKER] Frame sent")

    except Exception as e:
        logger.error(f"[TRACKER] Error: {e}")
    finally:
        await producer.stop()
        logger.info(f"[TRACKER] Kafka producer stopped")


async def start_tracking_process(camera_id):
    q = Queue()
    p = Process(target=tracking_loop, args=(camera_id, q))
    p.start()
    camera_queues[camera_id] = q
    camera_processes[camera_id] = p
    await mark_camera_alive(camera_id)


async def push_to_camera_queue(camera_id, data: ImageMessage):
    if camera_id not in camera_queues or not camera_processes[camera_id].is_alive():
        logger.info(f"[DISPATCHER] Starting new tracker for camera {camera_id}")
        await start_tracking_process(camera_id)

    await mark_camera_alive(camera_id)
    camera_queues[camera_id].put(data.model_dump())  # ensure it’s serializable
