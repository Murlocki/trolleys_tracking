from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, APIKeyHeader, HTTPAuthorizationCredentials
from socketio import AsyncServer, AsyncRedisManager, ASGIApp

from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.result_send_service_image.external_functions import check_auth_from_external_service, find_user_subscriptions

logger = setup_logger(__name__)

bearer = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"

sio = AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=logger,
    engineio_logger=logger,
    client_manager=AsyncRedisManager(redis_url),
)
socket_app = ASGIApp(sio)


async def get_valid_token(headers: dict,
                          credentials: HTTPAuthorizationCredentials | None = None,
                          api_key: str | None = None) -> str:
    logger.info(f"[AUTH] Headers: {headers}")
    if api_key == settings.api_key:
        return api_key
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing credentials")
    verify_result = await check_auth_from_external_service(credentials.credentials)
    logger.info(f"[AUTH] Verify result: {verify_result}")
    if not verify_result or not verify_result.get("token"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]

async def check_auth(api_key:str | None = None, token: str | None = None):
    logger.info(f"[AUTH] Token: {token} API Key: {api_key}")
    if api_key == settings.api_key:
        return api_key
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    verify_result = await check_auth_from_external_service(token)
    logger.info(f"[AUTH] Verify result: {verify_result}")
    if not verify_result or not verify_result.get("token"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]



@sio.event
async def connect(sid, environ, auth=None):
    try:
        # 1. Получаем заголовки напрямую
        scope_headers = environ.get("asgi.scope", {}).get("headers", [])
        headers = {k.decode(): v.decode() for k, v in scope_headers}

        # 2. Получаем токены
        authorization = headers.get("authorization", "")
        api_key = headers.get("x-api-key")
        camera_id = int(headers.get("x-cam"))
        logger.info(f"Auth headers: {headers}")
        class FakeCredentials:
            credentials = authorization.removeprefix("Bearer ")

        # 3. Проверяем авторизацию
        token = await get_valid_token(headers=headers, credentials=FakeCredentials(), api_key=api_key)

        # 4. Сохраняем сессию
        await sio.save_session(sid, {"api_key":api_key, "token": token})
        # 5. Извлекаем камеры для подписки
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        logger.info(f"User ID: {user_id}")

        await sio.enter_room(sid, camera_id)
        logger.info(f"Subscribed: user_id: {user_id} on camera_id:{camera_id}")

        logger.info(f"[CONNECT] Authorized sid={sid}")
        return True
    except Exception as e:
        logger.warning(f"[CONNECT] Authorization failed: {str(e)}")
        return False


@sio.event
async def disconnect(sid):
    logger.info(f"[DISCONNECT] sid={sid}")
    # Можно добавить очистку, если нужно
    # await sio.leave_room(sid)


async def validate_token_periodically():
    import asyncio

    while True:
        await asyncio.sleep(100)
        try:
            participants = sio.manager.get_participants("/", room=None)
            logger.info(f"[VALIDATE] participants={participants}")
        except Exception as e:
            logger.error(f"[AUTH CHECK] Failed to get participants: {e}")
            continue

        for participant in participants:
            sid, _ = participant
            logger.info(f"[VALIDATE] participant={participant}")
            try:
                session = await sio.get_session(sid)
                token = session.get("token")
                api_key = session.get("api_key")
                logger.info(f"[VALIDATE] session={session}")
                if not await check_auth(token=token, api_key=api_key):
                    logger.info(f"[AUTH CHECK] Invalid or expired token for sid={sid}, disconnecting")
                    await sio.disconnect(sid)
                logger.info(f"[VALIDATE] token={token} api_key={api_key}")
            except Exception as e:
                logger.warning(f"[AUTH CHECK] Error checking sid={sid}: {e}")

