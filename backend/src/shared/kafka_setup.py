import asyncio
import json
from pathlib import Path

from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema

from src.shared.config import settings


async def recreate_kafka_topics(topic_configs: dict[str, int], replication_factor: int = 1):
    admin = AdminClient({'bootstrap.servers': settings.kafka_broker})

    try:
        cluster_metadata = admin.list_topics(timeout=10)
        existing_topics = cluster_metadata.topics
    except Exception as e:
        print(f"[ERROR] Failed to connect to Kafka broker: {e}")
        return

    topics_to_delete = [t for t in topic_configs if t in existing_topics]

    if topics_to_delete:
        print(f"[INFO] Deleting existing topics: {topics_to_delete}")
        delete_fs = admin.delete_topics(topics_to_delete)
        for topic, f in delete_fs.items():
            try:
                f.result()
                print(f"[OK] Deletion initiated for topic: {topic}")
            except Exception as e:
                print(f"[ERROR] Failed to delete topic {topic}: {e}")

        for _ in range(10):
            remaining = admin.list_topics(timeout=10).topics
            if all(t not in remaining for t in topics_to_delete):
                break
            print("[WAIT] Waiting for topic deletion...")
            await asyncio.sleep(2)
        else:
            print("[ERROR] Timeout: Kafka did not delete topics in time.")
            return

    # Creating new topics
    topic_list = [NewTopic(t, num_partitions=p, replication_factor=replication_factor)
                  for t, p in topic_configs.items()]
    create_fs = admin.create_topics(topic_list)
    for topic, f in create_fs.items():
        try:
            f.result()
            print(f"[OK] Topic created: {topic}")
        except Exception as e:
            print(f"[ERROR] Failed to create topic {topic}: {e}")


def register_schema(subject: str, schema_path: str, schema_type: str = "AVRO"):
    registry_conf = {'url': settings.kafka_schema_registry}
    client = SchemaRegistryClient(registry_conf)

    path = Path(schema_path)
    if not path.exists():
        print(f"[ERROR] Schema file not found: {schema_path}")
        return

    schema_str = path.read_text()
    schema = Schema(schema_str, schema_type)

    try:
        schema_id = client.register_schema(subject, schema)
        print(f"[OK] Schema registered: {subject}, ID: {schema_id}")
    except Exception as e:
        print(f"[ERROR] Failed to register schema {subject}: {e}")


if __name__ == "__main__":
    asyncio.run(recreate_kafka_topics({
        settings.kafka_send_image_topic_name: settings.kafka_send_image_topic_partitions_count,
        settings.kafka_classification_topic_name: settings.kafka_classification_topic_partitions_count,
    }))

    # Укажи путь к схеме и subject:
    schema_file_path = "kafka-schemas/camera_message.avsc"
    schema_subject = f"send-images-value"
    register_schema(subject=schema_subject, schema_path=schema_file_path)
