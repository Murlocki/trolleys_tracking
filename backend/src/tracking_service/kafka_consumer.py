import asyncio
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import ImageMessage
from src.tracking_service.models.tracker_models import models_dict
from src.tracking_service.trackingProcess import push_to_camera_queue

logger = setup_logger(__name__)

schema_registry_conf = {'url': settings.kafka_schema_registry}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)
subject_name = settings.kafka_image_schema_name
schema_metadata = schema_registry_client.get_latest_version(subject_name)
avro_schema = schema_metadata.schema.schema_str
avro_deserializer = AvroDeserializer(schema_registry_client, avro_schema)

conf = {
    'bootstrap.servers': settings.kafka_broker,
    'group.id': 'tracking_consumer',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(conf)
consumer.subscribe([settings.kafka_tracking_topic_name])


async def consume_loop():
    try:
        logger.info("Starting consumer loop")
        loop = asyncio.get_running_loop()

        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error(f"Consumer error: {msg.error()}")
                continue

            context = SerializationContext(msg.topic(), MessageField.VALUE)
            value = avro_deserializer(msg.value(), context)
            if value is None:
                logger.error("Failed to deserialize message")
                continue

            try:
                image_msg = ImageMessage.model_validate(value)
            except Exception as e:
                logger.error(f"Invalid image message: {e}")
                continue

            regime = image_msg.activation_props.tracking_regime
            if models_dict.get(regime) is None:
                logger.warning(f"No model for regime {regime}")
                continue

            logger.info(f"Received message for camera {image_msg.camera_id}, regime {regime}")
            await push_to_camera_queue(image_msg.camera_id, image_msg)
    except Exception as e:
        logger.error(f"Consumer error: {str(e)}")