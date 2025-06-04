import json

from aiokafka import AIOKafkaProducer

from src.shared.config import settings
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)
# Инициализация продюсера
async def send_kafka_message(message: dict)-> dict|None:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_broker,
        value_serializer=lambda m: json.dumps(m).encode("utf-8")
    )
    try:
        await producer.start()
        logger.info(f"Start producing message: {message}")
        await producer.send_and_wait(settings.kafka_send_image_topic_name, message)
        logger.info(f"Message sent: {message}")
    except Exception as e:
        logger.error(e)
        return None
    finally:
        await producer.stop()
        logger.info(f"Stop producing message: {message}")
    return message