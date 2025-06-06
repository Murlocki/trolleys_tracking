from aiokafka import AIOKafkaConsumer

from src.result_send_service.websocket_router import sio
from src.shared.common_functions import decode_base64_image, encode_image_to_base64
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.redis_base import redis_client

logger = setup_logger(__name__)


import json

async def consume_kafka():
    consumer = AIOKafkaConsumer(
        settings.kafka_sending_topic_name,
        bootstrap_servers=settings.kafka_broker,
        group_id="socket_broadcast",
        auto_offset_reset="latest",
    )
    await consumer.start()
    logger.info("Consume send result start")

    try:
        async for msg in consumer:
            try:
                value = msg.value.decode()
                logger.info(f"Kafka message value: {value}")
                data = json.loads(value)

                camera_id = data.get("camera_id")
                if not camera_id:
                    logger.warning("No 'camera_id' in Kafka message")
                    continue

                queue_key = f"camera_result:{camera_id}"
                frame = await redis_client.lpop(queue_key)
                if not frame:
                    logger.warning(f"No frame found in Redis for {queue_key}")
                    continue
                try:
                    frame_data = json.loads(frame)
                except json.JSONDecodeError:
                    frame_data = frame  # Если это просто строка/байты, передаём как есть
                frame_data["image"] = decode_base64_image(frame_data["image"])
                frame_data["image"] = encode_image_to_base64(frame_data["image"])
                logger.info(f'Encoded and decoded frame data image: {frame_data["image"]}')
                await sio.emit("camera_frame", frame_data, room=camera_id)
                logger.info(f"Sent frame to room {camera_id}")

            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")

    except Exception as e:
        logger.error(f"Kafka consume error: {e}")

    finally:
        await consumer.stop()
