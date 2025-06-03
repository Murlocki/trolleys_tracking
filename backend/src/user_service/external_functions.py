import httpx
from httpx import Response

from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse
from src.user_service.endpoints import CHECK_AUTH, DELETE_USER_SESSIONS

logger = setup_logger(__name__)


async def check_auth_from_external_service(access_token: str) -> TokenModelResponse | None:
    """
    Check auth
    :param access_token:
    :return: json - token old or new
    """
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(CHECK_AUTH, headers=headers)
            response.raise_for_status()  # Проверяем статусный код на ошибки
            json_data = response.json()
            return json_data
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None


async def delete_user_sessions(user_id: int, api_key: str) -> Response:
    """
    Check auth
    :param user_id:
    :param api_key:
    :return: json - token old or new
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DELETE_USER_SESSIONS}/{user_id}", headers=headers)
        logger.info(f"Deleted user sessions with response {response}")
        return response
