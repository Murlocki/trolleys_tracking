import asyncio
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import ImageMessage

logger = setup_logger(__name__)

schema_registry_conf = {'url': settings.kafka_schema_registry}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

subject_name = settings.kafka_image_schema_name
schema_info = schema_registry_client.get_latest_version(subject_name)
schema_str = schema_info.schema.schema_str
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {'bootstrap.servers': settings.kafka_broker}
producer = Producer(producer_conf)

class SerializationContext:
    def __init__(self, topic: str):
        self.topic = topic
        self.field = "value"

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_sync(message: ImageMessage, partition: int | None = None, topic: str = None):
    ctx = SerializationContext(topic)
    value_bytes = avro_serializer(message.model_dump(by_alias=True), ctx)
    producer.produce(
        topic=topic,
        value=value_bytes,
        partition=partition,
        callback=delivery_report
    )
    producer.flush()

async def produce_async(message: ImageMessage, partition: int | None = None, topic: str = None):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, produce_sync, message, partition, topic)
