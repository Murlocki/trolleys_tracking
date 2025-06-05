import asyncio

from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from src.detection_service.kafka_producer import produce_async
from src.detection_service.models.detection_models import models_dict
from src.shared.common_functions import decompress_image, get_partition
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import ImageMessage, BoundingBox

logger = setup_logger(__name__)

schema_registry_conf = {'url': settings.kafka_schema_registry}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Название субъекта схемы в Registry (обычно topic-value)
subject_name = f"send-images-value"

# Получаем последнюю версию схемы из Registry
schema_metadata = schema_registry_client.get_latest_version(subject_name)
avro_schema = schema_metadata.schema.schema_str

avro_deserializer = AvroDeserializer(schema_registry_client, avro_schema)

conf = {
    'bootstrap.servers': settings.kafka_broker,
    'group.id': 'camera-image-consumer-group',
    'auto.offset.reset': 'earliest',
}
consumer = Consumer(conf)
consumer.subscribe([settings.kafka_send_image_topic_name])


async def consume_loop():
    logger.info("Starting consumer")
    loop = asyncio.get_running_loop()
    while True:
        msg = await loop.run_in_executor(None, consumer.poll, 1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logger.error(f"Consumer error: {msg.error()}")
                continue

        context = SerializationContext(msg.topic(), MessageField.VALUE)
        value = avro_deserializer(msg.value(), context)
        if value is None:
            logger.error("Failed to deserialize message")
            continue

        logger.info("Received message:")
        image_msg = ImageMessage.model_validate(value)

        regime = image_msg.activation_props.detection_regime
        model = models_dict.get(regime)
        if model is None:
            logger.warning(f"No model for regime {regime}")
            continue
        logger.info(f"Set detection model: {model}")

        # TODO: Раскоментить на проде
        image = decompress_image(image_msg.image)
        #results = model.process_image(image)
        #bboxes = model.process_bounding_box(results)
        #image_msg.bounding_boxes = bboxes or []
        image_msg.bounding_boxes = [
            BoundingBox(
                x=1,
                y=1,
                width=10,
                height=11
            )
        ]

        logger.info(f"Processed image")
        await produce_async(
            image_msg,
            get_partition(
                camera_id=image_msg.camera_id,
                num_partitions=settings.kafka_classification_topic_partitions_count
            ),
            topic=settings.kafka_classification_topic_name
        )
        logger.info(f"Sent message to classification")
