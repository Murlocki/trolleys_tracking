import httpx
from httpx import Response

from src.auth_service.endpoints import CREATE_SESSION, GET_SESSION_BY_TOKEN, UPDATE_SESSION_TOKEN, DELETE_SESSION, \
    AUTHENTICATE_USER, DELETE_SESSION_BY_TOKEN, FIND_USER_BY_USERNAME, FIND_USER_BY_ID
from src.shared.logger_setup import setup_logger
from src.shared.schemas import SessionSchema, AccessTokenUpdate, UserAuthDTO

logger = setup_logger(__name__)


async def create_session(session_data: SessionSchema, api_key: str) -> Response:
    """
    Create a session by forwarding data to external service.
    :param api_key: api key
    :param session_data: Session data
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    logger.info(f"Creating session with data: {session_data}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            CREATE_SESSION,
            headers=headers,
            content=session_data.model_dump_json()
        )
        logger.info(f"Created session with response: {response.json()}")
        return response


async def get_session_by_token(api_key: str, token: str, token_type: str = "access_token") -> Response:
    """
    Получить сессию по токену из внешнего сервиса.
    :param api_key: api key
    :param token: Token for finding session
    :param token_type: Token type for finding session
    :return response: Response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GET_SESSION_BY_TOKEN}?token={token}&token_type={token_type}",
            headers=headers
        )
        logger.info(f"Get session by token {token} with type {token_type} with response: {response.json()}")
        return response


async def update_session_token(api_key: str, session_id: str, user_id:int, access_token_update_data: AccessTokenUpdate) -> Response:
    """
    Update session token by forwarding data to external service.
    :param api_key: api key
    :param user_id: session user id
    :param session_id: session id for updating session
    :param access_token_update_data: new access token update data
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{UPDATE_SESSION_TOKEN}/{user_id}/{session_id}/update_token",
            headers=headers,
            content=access_token_update_data.model_dump_json()
        )
        logger.info(f"Updated session token: {response.json()}")
        return response


async def delete_session_by_id(api_key: str, session_id: str, user_id: int) -> Response:
    """
    Delete session by id
    :param user_id: session user id
    :param api_key: api key
    :param session_id: session id for deleting
    :return: response from external service
    """
    async with httpx.AsyncClient() as client:
        headers = {
            "content-type": "application/json",
            "X-API-Key": api_key,
        }
        response = await client.delete(
            f"{DELETE_SESSION}/{user_id}/{session_id}",
            headers=headers
        )
        logger.info(f"Deleted session {session_id} with response: {response.json()}")
        return response


async def delete_sessions_by_token(api_key: str, access_token: str, skip_auth: bool = False) -> Response:
    """
    Delete session by token
    :param api_key: api key
    :param access_token: token for finding session
    :param skip_auth: need check auth in method
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "authorization": f"bearer {access_token}",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DELETE_SESSION_BY_TOKEN}",
            headers=headers
        )
        logger.info(f"Deleted sessions by token {access_token} with response {response.json()}")
        return response


async def authenticate_user(user: UserAuthDTO, api_key: str) -> Response:
    """
    Authenticate user
    :param api_key: service api key
    :param user: User identifier and password
    :return: Auth response
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    logger.info(headers)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTHENTICATE_USER}",
            headers=headers,
            content=user.model_dump_json()
        )
        logger.info(f"Authenticated user response {response.json()}")
        return response


async def find_user_by_id(user_id: int, api_key: str) -> Response:
    """
    Find user by username
    :param api_key: api key
    :param user_id: username for finding user
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FIND_USER_BY_ID}/{user_id}",
            headers=headers,
        )
        logger.info(f"Find user by user_id: {user_id} with response {response.json()}")
        return response