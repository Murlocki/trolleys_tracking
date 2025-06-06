import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.detection_service.kafka_consumer import consume_loop
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)
# Глобально доступная переменная для схемы
avro_schema = None
# kafka-consumer-groups.sh --bootstrap-server localhost:9093 --topic track_images --group tracking_consumer --reset-offsets --to-earliest --execute
# kafka-consumer-groups.sh  --bootstrap-server localhost:9093 --delete --group tracking_consumer
# kafka-consumer-groups.sh --bootstrap-server localhost:9093 --topic send_result --group socket_broadcast --reset-offsets --to-earliest --execute
@asynccontextmanager
async def lifespan(app: FastAPI):
    global avro_schema

    logger.info("Lifespan startup: loading Avro schema and launching Kafka consumer")
    # Запуск фоновой задачи Kafka consumer
    task = asyncio.create_task(consume_loop())

    yield

    # Завершаем consumer по завершении приложения
    logger.info("Shutting down Kafka consumer task")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled")



app = FastAPI(lifespan=lifespan)


