import httpx
from httpx import Response

from src.session_service.endpoints import CHECK_AUTH, FIND_USER_BY_USERNAME
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse

logger = setup_logger(__name__)


async def check_auth_from_external_service(access_token: str, skip_auth: bool = False) -> TokenModelResponse | None:
    """
    Check auth
    :param skip_auth:
    :param access_token:
    :return: json - token old or new
    """
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
            "X-Skip-Auth": str(skip_auth)
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


async def find_user_by_username(username: str, api_key:str) -> Response:
    """
    Find user by username
    :param api_key: api key of service
    :param username: email to find
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FIND_USER_BY_USERNAME}?username={username}",
            headers=headers,
        )
        logger.info(f"Find user by username: {username} with response {response.json()}")
        return response
