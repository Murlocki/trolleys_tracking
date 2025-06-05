import asyncio
from confluent_kafka import Consumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from src.shared.config import settings


async def consume():
    schema_registry_conf = {'url': settings.kafka_schema_registry}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # Название субъекта схемы в Registry (обычно topic-value)
    subject_name = f"{settings.kafka_send_image_topic_name}-value"

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

    loop = asyncio.get_running_loop()
    try:
        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    continue

            context = SerializationContext(msg.topic(), MessageField.VALUE)
            value = avro_deserializer(msg.value(), context)
            if value is None:
                print("Failed to deserialize message")
                continue

            print("Received message:")
            print(value)

    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        consumer.close()


if __name__ == "__main__":
    asyncio.run(consume())
