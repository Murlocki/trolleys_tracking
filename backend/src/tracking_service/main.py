import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.shared.logger_setup import setup_logger
from src.tracking_service.kafka_consumer import consume_loop

logger = setup_logger(__name__)
# Глобально доступная переменная для схемы
avro_schema = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global avro_schema

    logger.info("Lifespan startup: loading Avro schema and launching Kafka consumer")
    task = asyncio.create_task(consume_loop())

    yield

    # Завершаем consumer по завершении приложения
    logger.info("Shutting down Kafka consumer task")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled")
    except Exception as e:
        raise e



app = FastAPI(lifespan=lifespan)


