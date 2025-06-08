import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.result_send_service.websocket_router import sio, socket_app, validate_token_periodically
from src.result_send_service.kafka_consumer import consume_kafka


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka_task = asyncio.create_task(consume_kafka())
    auth_check_task = asyncio.create_task(validate_token_periodically())
    yield
    kafka_task.cancel()
    auth_check_task.cancel()
    await asyncio.gather(kafka_task, auth_check_task, return_exceptions=True)


app = FastAPI(title="Result WebSocket Service", lifespan=lifespan)
app.mount("/", socket_app)

