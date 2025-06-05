import json
from aiokafka import AIOKafkaProducer
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client
from src.shared.schemas import ImageMessage
import base64
logger = setup_logger(__name__)

producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_broker)

async def produce_message(message: ImageMessage):
    try:
        logger.info("Started producer")
        message_to_redis = message.model_dump()
        message_to_redis["image"] = base64.b64encode(message.image).decode("utf-8")
        logger.info("Created message to redis")
        await redis_client.rpush(f"camera_result:{message.camera_id}", json.dumps(message_to_redis))
        logger.info("Send result message to redis")
        await producer.send_and_wait(
            topic=settings.kafka_sending_topic_name,
            value=json.dumps({"camera_id":message.camera_id}).encode("utf-8"),
        )
        logger.info("Send result message in kafka topic")
    except Exception as e:
        logger.error(e)