import asyncio
from concurrent.futures import ThreadPoolExecutor

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer

from src.shared.config import settings

# Инициализация клиента Schema Registry и сериализатора (один раз)
schema_registry_conf = {'url': settings.kafka_schema_registry}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

subject_name = settings.kafka_send_image_topic_name + "-value"
schema_info = schema_registry_client.get_latest_version(subject_name)
schema_str = schema_info.schema.schema_str
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {'bootstrap.servers': settings.kafka_broker}
producer = Producer(producer_conf)

class SerializationContext:
    def __init__(self, topic):
        self.topic = topic
        self.field = "value"

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_sync(message: dict):
    ctx = SerializationContext(settings.kafka_send_image_topic_name)
    value_bytes = avro_serializer(message, ctx)
    producer.produce(settings.kafka_send_image_topic_name, value=value_bytes, callback=delivery_report)
    producer.flush()

async def produce_async(message: dict):
    """Асинхронный вызов синхронной функции в отдельном потоке"""
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, produce_sync, message)

# Пример использования
async def main():
    test_message = {
        "camera_id": 1,
        "timestamp": 1685923200,
        "meta": "test metadata",
        "image": b"\x89PNG\r\n\x1a\n",
        "activation_props":{
            "detection_regime": "yoloV8x",
            "classification_regime": "yoloV8x",
            "tracking_regime": "deepsort"
        }
    }
    await produce_async(test_message)

if __name__ == "__main__":
    asyncio.run(main())
